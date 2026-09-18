import re
filepath = 'python_engine/app/services/ai_service.py'
with open(filepath, 'r') as f:
    content = f.read()

pattern = r'''            # Perform Bengali Translation
            input_ids = self\.translation_tokenizer\("translate English to Bengali: " \+ text, return_tensors="pt"\)\.input_ids
            outputs = self\.translation_model\.generate\(input_ids, max_length=128\)
            bn_translation = self\.translation_tokenizer\.decode\(outputs\[0\], skip_special_tokens=True\)'''

replacement = '''            # Perform Bengali Translation ONLY if it's an Idiom or Hard Word to save CPU time!
            bn_translation = ""
            if target_word != "None":
                input_ids = self.translation_tokenizer("translate English to Bengali: " + text, return_tensors="pt").input_ids
                outputs = self.translation_model.generate(input_ids, max_length=128)
                bn_translation = self.translation_tokenizer.decode(outputs[0], skip_special_tokens=True)'''

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)
print("Speed Patch applied successfully!")
