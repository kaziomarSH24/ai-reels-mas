import re
filepath = 'python_engine/app/services/ai_service.py'
with open(filepath, 'r') as f:
    content = f.read()

# Remove the translation block completely
pattern = r'# Perform Bengali Translation ONLY.*?bn_translation = ""\s*if target_word != "None":\s*input_ids = self\.translation_tokenizer\(text, return_tensors="pt"\)\.input_ids\s*outputs = self\.translation_model\.generate\(input_ids, max_length=128\)\s*bn_translation = self\.translation_tokenizer\.decode\(outputs\[0\], skip_special_tokens=True\)'
replacement = 'bn_translation = "Will translate during reel generation..."'

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)
print("T5 Removed!")
