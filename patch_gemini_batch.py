import re

with open("python_engine/app/services/ai_service.py", "r") as f:
    content = f.read()

old_gemini_logic = """        # 2. Batch Translate with Gemini
        print("[AIService] Sending BATCH translation request to Gemini...")
        api_key = os.environ.get("GEMINI_API_KEY")
        success = False
        
        if api_key:
            prompt = (
                "You are an expert English to Bengali translator. "
                "I will give you a JSON array of English movie dialogues. "
                "Translate each dialogue into casual, natural Bengali. "
                "Return ONLY a valid JSON array of strings containing the Bengali translations, in the EXACT same order. "
                f"Dialogues: {json.dumps(texts)}"
            )
            
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.1} # Low temp for JSON stability
            }
            
            import requests
            gemini_models = ["gemini-3.8-flash", "gemini-3.6-flash", "gemini-3.5-flash"]
            for model in gemini_models:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                try:
                    response = requests.post(url, json=payload, timeout=45) # 45s timeout for large batches
                    response.raise_for_status()
                    data = response.json()
                    
                    raw_text = data['candidates'][0]['content']['parts'][0]['text']
                    
                    # Clean markdown code blocks if present
                    if raw_text.startswith("```json"):
                        raw_text = raw_text.strip("```json").strip("```").strip()
                    elif raw_text.startswith("```"):
                        raw_text = raw_text.strip("```").strip()
                        
                    translations = json.loads(raw_text)
                    
                    if len(translations) == len(texts):
                        for i in range(len(texts)):
                            results[i]['translation'] = translations[i]
                        success = True
                        print(f"[AIService] Successfully batch translated {len(texts)} items using {model}")
                        break
                    else:
                        print(f"[AIService] Gemini returned wrong number of translations ({len(translations)} vs {len(texts)})")
                except Exception as e:
                    print(f"[AIService] Batch Gemini failed with {model}: {str(e)}")"""

new_gemini_logic = """        # 2. Batch Translate with Gemini in Chunks (to support 1+ hour videos)
        print(f"[AIService] Sending BATCH translation request to Gemini for {len(texts)} items...")
        api_key = os.environ.get("GEMINI_API_KEY")
        success = False
        
        if api_key:
            import requests
            import time
            success = True
            
            # Chunk the texts into batches of 150 to avoid Gemini output token limits (8192 max)
            chunk_size = 150
            for chunk_start in range(0, len(texts), chunk_size):
                chunk_end = min(chunk_start + chunk_size, len(texts))
                texts_chunk = texts[chunk_start:chunk_end]
                print(f"[AIService] Processing Gemini Batch: {chunk_start} to {chunk_end}...")
                
                prompt = (
                    "You are an expert English to Bengali translator. "
                    "I will give you a JSON array of English movie dialogues. "
                    "Translate each dialogue into casual, natural Bengali. "
                    "Return ONLY a valid JSON array of strings containing the Bengali translations, in the EXACT same order. "
                    f"Dialogues: {json.dumps(texts_chunk)}"
                )
                
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.1}
                }
                
                chunk_success = False
                gemini_models = ["gemini-1.5-flash", "gemini-1.5-pro"]
                for model in gemini_models:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                    try:
                        response = requests.post(url, json=payload, timeout=60)
                        response.raise_for_status()
                        data = response.json()
                        
                        raw_text = data['candidates'][0]['content']['parts'][0]['text']
                        
                        if raw_text.startswith("```json"):
                            raw_text = raw_text.strip("```json").strip("```").strip()
                        elif raw_text.startswith("```"):
                            raw_text = raw_text.strip("```").strip()
                            
                        translations = json.loads(raw_text)
                        
                        if len(translations) == len(texts_chunk):
                            for i, t in enumerate(translations):
                                results[chunk_start + i]['translation'] = t
                            chunk_success = True
                            print(f"[AIService] Successfully translated chunk using {model}")
                            break
                    except Exception as e:
                        print(f"[AIService] Chunk translation failed with {model}: {str(e)}")
                        
                if not chunk_success:
                    success = False
                    break
                    
                # Small delay to avoid API rate limits
                time.sleep(2)"""

content = content.replace(old_gemini_logic, new_gemini_logic)

with open("python_engine/app/services/ai_service.py", "w") as f:
    f.write(content)
