import os
import warnings
from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
from dotenv import load_dotenv

load_dotenv('/var/www/.env')
warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

class AIService:
    _instance = None
    
    def __new__(cls):
        """
        Singleton pattern to ensure models are only loaded once into memory
        across all API requests.
        """
        if cls._instance is None:
            cls._instance = super(AIService, cls).__new__(cls)
            cls._instance._initialize_models()
        return cls._instance
        
    def _initialize_models(self):
        """
        Loads all required machine learning models into RAM during server boot.
        This eliminates the delay of disk I/O on every API request.
        """
        print("[AIService] Booting up AI Agents...")
        
        # Adjust path to reach the root 'python_engine' folder from 'app/services'
        script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # 1. Load Emotion Model
        print("Loading Emotion Model...")
        emotion_model_path = os.path.join(script_dir, "models", "emotion_model")
        self.emotion_classifier = pipeline(
            "text-classification", 
            model=emotion_model_path, 
            tokenizer=emotion_model_path
        )
        print("Emotion Model Ready!")
        
        # 2. Load Translation Model
        print("Loading Translation Model...")
        translation_model_name = "csebuetnlp/banglat5_nmt_en_bn"
        self.translation_tokenizer = AutoTokenizer.from_pretrained(translation_model_name, use_fast=False)
        self.translation_model = AutoModelForSeq2SeqLM.from_pretrained(translation_model_name)
        print("Translation Model Ready!")

        # 3. Load CEFR Difficulty Model
        print("Loading CEFR Difficulty Model...")
        cefr_model_path = os.path.join(script_dir, "models", "word_level_cefr_model")
        self.cefr_classifier = pipeline(
            "token-classification", 
            model=cefr_model_path, 
            tokenizer=cefr_model_path,
            aggregation_strategy="simple"
        )
        print("CEFR Difficulty Model Ready!")

    def _translate_with_gemini(self, text: str, model_name: str) -> str:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment.")
            
        import requests
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        
        prompt = f"Translate the following English movie dialogue into casual, natural, and conversational Bengali. Provide ONLY the Bengali translation, nothing else. Dialogue: '{text}'"
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.3}
        }
        
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        return data['candidates'][0]['content']['parts'][0]['text'].strip()

    def analyze_dialogue(self, text: str):
        pass # Not used in batch mode anymore

    def batch_analyze_dialogues(self, texts: list[str]):
        """
        Takes a list of texts and processes them all at once.
        Runs Emotion and CEFR locally.
        Sends ALL texts to Gemini in ONE single JSON prompt to bypass rate limits and save time.
        """
        import json
        
        results = []
        
        # 1. Run Local Models (Emotion & CEFR) - Fast on CPU
        print(f"[AIService] Running Local AI for {len(texts)} dialogues...")
        level_scores = {"A1": 1, "A2": 2, "B1": 3, "B2": 4, "C1": 5, "C2": 6}
        
        for text in texts:
            emotion_res = self.emotion_classifier(text)[0]
            
            # Word-level CEFR classification
            cefr_tokens = self.cefr_classifier(text)
            
            # Find the hardest word
            hardest_word = None
            highest_level = "A1"
            highest_score = 1
            confidence = 0.0
            
            for token in cefr_tokens:
                lbl = token['entity_group']
                score = level_scores.get(lbl, 1)
                if score > highest_score:
                    highest_score = score
                    highest_level = lbl
                    hardest_word = token['word'].strip()
                    confidence = float(token['score'])
                # Break ties by taking the longer word
                elif score == highest_score and hardest_word and len(token['word'].strip()) > len(hardest_word):
                    hardest_word = token['word'].strip()
                    confidence = float(token['score'])
                    
            if not hardest_word: # Fallback if empty string
                highest_level = "A1"
                hardest_word = "None"
                confidence = 1.0
            
            results.append({
                "text": text,
                "emotion": emotion_res['label'].upper(),
                "emotion_confidence": round(emotion_res['score'] * 100, 2),
                "cefr_level": highest_level,
                "cefr_confidence": round(confidence * 100, 2),
                "target_word": hardest_word,
                "translation": "" # Will fill in next step
            })
            
        # 2. Batch Translate with Gemini in Chunks (to support 1+ hour videos)
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
                    "You are an expert English editor and Bengali translator. "
                    "I will give you a JSON array of raw, auto-generated English movie dialogues (which lack punctuation). "
                    "For each dialogue, first FIX the English text by adding proper punctuation (commas, periods, question marks) and capitalization. "
                    "Then, translate it into casual, natural Bengali. "
                    "Return ONLY a valid JSON array of OBJECTS, where each object has two keys: 'english' (the fixed text) and 'bengali' (the translation). "
                    "Must be in the EXACT same order and same length as the input. "
                    f"Dialogues: {json.dumps(texts_chunk)}"
                )
                
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.1}
                }
                
                chunk_success = False
                gemini_models = ["gemini-3.6-flash", "gemini-3.5-flash"]
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
                            for i, resp in enumerate(translations):
                                if isinstance(resp, dict):
                                    results[chunk_start + i]['fixed_english'] = resp.get('english', texts_chunk[i])
                                    results[chunk_start + i]['translation'] = resp.get('bengali', '')
                                else:
                                    results[chunk_start + i]['translation'] = resp
                                    results[chunk_start + i]['fixed_english'] = texts_chunk[i]
                            chunk_success = True
                            print(f"[AIService] Successfully translated and punctuated chunk using {model}")
                            break
                    except Exception as e:
                        print(f"[AIService] Chunk translation failed with {model}: {str(e)}")
                        
                if not chunk_success:
                    success = False
                    break
                    
                # Small delay to avoid API rate limits
                time.sleep(2)
                    
        # 3. Fallback to Local BanglaT5 if Gemini completely fails
        if not success:
            print("[AIService] Gemini Batch Failed! Falling back to slow Local BanglaT5...")
            for i, text in enumerate(texts):
                inputs = self.translation_tokenizer(text, return_tensors="pt")
                generated_tokens = self.translation_model.generate(**inputs, max_length=100)
                results[i]['translation'] = self.translation_tokenizer.decode(generated_tokens[0], skip_special_tokens=True)
                
        return results

# Global singleton instance for the FastAPI application
ai_agent = AIService()
