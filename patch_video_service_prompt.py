import re

with open("python_engine/app/services/video_service.py", "r") as f:
    content = f.read()

old_prompt_code = """        prompt = (
            f"You are a helpful dictionary and translator. The user wants a short, punchy video subtitle for the word '{target_word}'. "
            f"The full subtitle is: '{english_text}'. "
            "1. Extract ONLY the exact sentence that contains the target word (remove surrounding unnecessary context). "
            "2. Translate that exact short sentence into natural Bengali. "
            f"3. Provide the exact dictionary meaning in Bengali for the specific word '{target_word}'. "
            "Return ONLY a valid JSON object with keys: 'short_english', 'short_bengali', 'target_word_bengali_meaning'."
        )"""

new_prompt_code = """        prompt = (
            f"You are an expert English-to-Bengali translator. The target vocabulary word is '{target_word}'. "
            f"The full subtitle context is: '{english_text}'. "
            "Follow these strict rules:\\n"
            "1. 'short_english': Extract ONLY the exact short sentence containing the target word.\\n"
            "2. 'target_word_bengali_meaning': Provide the exact Bengali dictionary meaning of the target word in this context (e.g. for 'asthmatic' use 'হাঁপানি রোগী'). MUST NOT BE EMPTY.\\n"
            "3. 'short_bengali': Translate the 'short_english' into natural, grammatically correct Bengali.\\n"
            "4. CRITICAL: The exact word(s) you use for 'target_word_bengali_meaning' MUST be present inside the 'short_bengali' sentence so I can highlight it!\\n"
            "Return ONLY a valid JSON object with EXACTLY these 3 keys: 'short_english', 'short_bengali', 'target_word_bengali_meaning'."
        )"""

content = content.replace(old_prompt_code, new_prompt_code)

with open("python_engine/app/services/video_service.py", "w") as f:
    f.write(content)
