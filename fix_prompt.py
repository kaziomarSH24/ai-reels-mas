import re
filepath = 'python_engine/app/services/video_service.py'
with open(filepath, 'r') as f:
    content = f.read()

target = '''Return ONLY the direct dictionary meaning of "{target}" in Bengali.
Keep it extremely short (max 2-3 words). 
Example: "খুব সহজ", "বিপাকে পড়া", "যোগাযোগ".
Return nothing else."""'''

replacement = '''Return ONLY the true, contextual dictionary meaning of "{target}" in Bengali.
WARNING: If it is an idiom (like 'piece of cake'), return the FIGURATIVE meaning (e.g. 'খুব সহজ'). DO NOT translate it literally (e.g. do not say 'এক টুকরো কেক').
Keep it extremely short (max 2-3 words). 
Return nothing else."""'''

content = content.replace(target, replacement)
with open(filepath, 'w') as f:
    f.write(content)
print("Prompt updated!")
