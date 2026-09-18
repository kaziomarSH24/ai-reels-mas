import re
filepath = 'python_engine/app/services/ai_service.py'
with open(filepath, 'r') as f:
    content = f.read()

pattern = r'self\.translation_tokenizer\("translate English to Bengali: " \+ text, return_tensors="pt"\)\.input_ids'
replacement = 'self.translation_tokenizer(text, return_tensors="pt").input_ids'

content = re.sub(pattern, replacement, content)

with open(filepath, 'w') as f:
    f.write(content)
print("T5 Patch applied!")
