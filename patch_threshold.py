filepath = 'python_engine/app/services/ai_service.py'
with open(filepath, 'r') as f:
    content = f.read()

# Replace threshold logic
old_logic = '''                # Confidence Filter
                if float(token['score']) < 0.85:
                    continue'''

new_logic = '''                # Confidence Filter
                score = float(token['score'])
                if lbl == 'IDIOM' and score < 0.50:
                    continue
                elif lbl == 'HARD_WORD' and score < 0.70:
                    continue'''

content = content.replace(old_logic, new_logic)

with open(filepath, 'w') as f:
    f.write(content)

print("Patch applied successfully!")
