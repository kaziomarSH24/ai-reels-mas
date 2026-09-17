import re

with open("python_engine/app/services/ai_service.py", "r") as f:
    content = f.read()

old_prompt = """                prompt = (
                    "You are an expert English to Bengali translator. "
                    "I will give you a JSON array of English movie dialogues. "
                    "Translate each dialogue into casual, natural Bengali. "
                    "Return ONLY a valid JSON array of strings containing the Bengali translations, in the EXACT same order. "
                    f"Dialogues: {json.dumps(texts_chunk)}"
                )"""

new_prompt = """                prompt = (
                    "You are an expert English editor and Bengali translator. "
                    "I will give you a JSON array of raw, auto-generated English movie dialogues (which lack punctuation). "
                    "For each dialogue, first FIX the English text by adding proper punctuation (commas, periods, question marks) and capitalization. "
                    "Then, translate it into casual, natural Bengali. "
                    "Return ONLY a valid JSON array of OBJECTS, where each object has two keys: 'english' (the fixed text) and 'bengali' (the translation). "
                    "Must be in the EXACT same order and same length as the input. "
                    f"Dialogues: {json.dumps(texts_chunk)}"
                )"""

old_parse = """                        if len(translations) == len(texts_chunk):
                            for i, t in enumerate(translations):
                                results[chunk_start + i]['translation'] = t
                            chunk_success = True
                            print(f"[AIService] Successfully translated chunk using {model}")"""

new_parse = """                        if len(translations) == len(texts_chunk):
                            for i, resp in enumerate(translations):
                                if isinstance(resp, dict):
                                    results[chunk_start + i]['fixed_english'] = resp.get('english', texts_chunk[i])
                                    results[chunk_start + i]['translation'] = resp.get('bengali', '')
                                else:
                                    results[chunk_start + i]['translation'] = resp
                                    results[chunk_start + i]['fixed_english'] = texts_chunk[i]
                            chunk_success = True
                            print(f"[AIService] Successfully translated and punctuated chunk using {model}")"""

content = content.replace(old_prompt, new_prompt).replace(old_parse, new_parse)

with open("python_engine/app/services/ai_service.py", "w") as f:
    f.write(content)

with open("python_engine/app/controllers/ai_controller.py", "r") as f:
    ctrl = f.read()

old_ctrl_acc = """                accepted.append({
                    "start_time": item['start_time'],
                    "end_time": item['end_time'],
                    "text": item['text'],
                    "analysis": full_analysis
                })"""

new_ctrl_acc = """                accepted.append({
                    "start_time": item['start_time'],
                    "end_time": item['end_time'],
                    "text": full_analysis.get('fixed_english', item['text']),
                    "analysis": full_analysis
                })"""

old_ctrl_rej = """                rejected.append({
                    "start_time": item['start_time'],
                    "end_time": item['end_time'],
                    "text": item['text'],
                    "analysis": full_analysis
                })"""

new_ctrl_rej = """                rejected.append({
                    "start_time": item['start_time'],
                    "end_time": item['end_time'],
                    "text": full_analysis.get('fixed_english', item['text']),
                    "analysis": full_analysis
                })"""

ctrl = ctrl.replace(old_ctrl_acc, new_ctrl_acc).replace(old_ctrl_rej, new_ctrl_rej)

with open("python_engine/app/controllers/ai_controller.py", "w") as f:
    f.write(ctrl)

