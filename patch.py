import re

with open("python_engine/app/services/ai_service.py", "r") as f:
    content = f.read()

# 1. Update Model Loading
content = content.replace(
    'cefr_model_path = os.path.join(script_dir, "models", "cefr_model")',
    'cefr_model_path = os.path.join(script_dir, "models", "word_level_cefr_model")'
)
content = content.replace(
    'self.cefr_classifier = pipeline(\n            "text-classification", \n            model=cefr_model_path, \n            tokenizer=cefr_model_path\n        )',
    'self.cefr_classifier = pipeline(\n            "token-classification", \n            model=cefr_model_path, \n            tokenizer=cefr_model_path,\n            aggregation_strategy="simple"\n        )'
)

# 2. Update Inference Logic
inference_old = """        for text in texts:
            emotion_res = self.emotion_classifier(text)[0]
            cefr_res = self.cefr_classifier(text)[0]
            
            results.append({
                "text": text,
                "emotion": emotion_res['label'].upper(),
                "emotion_confidence": round(emotion_res['score'] * 100, 2),
                "cefr_level": cefr_res['label'].upper(),
                "cefr_confidence": round(cefr_res['score'] * 100, 2),
                "translation": "" # Will fill in next step
            })"""

inference_new = """        level_scores = {"A1": 1, "A2": 2, "B1": 3, "B2": 4, "C1": 5, "C2": 6}
        
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
                    confidence = token['score']
                # Break ties by taking the longer word
                elif score == highest_score and hardest_word and len(token['word'].strip()) > len(hardest_word):
                    hardest_word = token['word'].strip()
                    confidence = token['score']
                    
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
            })"""

content = content.replace(inference_old, inference_new)

with open("python_engine/app/services/ai_service.py", "w") as f:
    f.write(content)
