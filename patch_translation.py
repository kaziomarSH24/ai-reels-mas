import os

filepath = 'python_engine/app/services/ai_service.py'
with open(filepath, 'r') as f:
    content = f.read()

# Replace the empty translation logic
old_logic = '''            results.append({
                "text": text,
                "emotion": emotion_res['label'].upper(),
                "emotion_confidence": round(emotion_res['score'] * 100, 2),
                "cefr_level": highest_level,
                "cefr_confidence": round(confidence * 100, 2),
                "target_word": target_word,
                "translation": "", 
                "fixed_english": text 
            })'''

new_logic = '''            # Perform Bengali Translation
            input_ids = self.translation_tokenizer("translate English to Bengali: " + text, return_tensors="pt").input_ids
            outputs = self.translation_model.generate(input_ids, max_length=128)
            bn_translation = self.translation_tokenizer.decode(outputs[0], skip_special_tokens=True)

            results.append({
                "text": text,
                "emotion": emotion_res['label'].upper(),
                "emotion_confidence": round(emotion_res['score'] * 100, 2),
                "cefr_level": highest_level,
                "cefr_confidence": round(confidence * 100, 2),
                "target_word": target_word,
                "translation": bn_translation, 
                "fixed_english": text 
            })'''

content = content.replace(old_logic, new_logic)

with open(filepath, 'w') as f:
    f.write(content)

print("Translation Patch applied successfully!")
