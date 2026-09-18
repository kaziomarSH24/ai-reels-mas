import re

# Update Pydantic model
filepath_controller = 'python_engine/app/controllers/ai_controller.py'
with open(filepath_controller, 'r') as f:
    c = f.read()
c = c.replace("target_word: str", "target_word: str\n    dictionary_meaning: str | None = None")
with open(filepath_controller, 'w') as f:
    f.write(c)

# Update video service
filepath_service = 'python_engine/app/services/video_service.py'
with open(filepath_service, 'r') as f:
    s = f.read()

target_service = '''            if target in gemini_cache:
                short_eng, short_ben, word_meaning = gemini_cache[target]
            else:
                short_eng, short_ben, word_meaning = self._get_gemini_shortened_text(target, eng_text, ben_text)
                gemini_cache[target] = (short_eng, short_ben, word_meaning)'''

replacement_service = '''            dict_meaning = str(clip.get('dictionary_meaning', '')).strip()
            if dict_meaning:
                short_eng = ""
                short_ben = ""
                word_meaning = dict_meaning
            else:
                if target in gemini_cache:
                    short_eng, short_ben, word_meaning = gemini_cache[target]
                else:
                    short_eng, short_ben, word_meaning = self._get_gemini_shortened_text(target, eng_text, ben_text)
                    gemini_cache[target] = (short_eng, short_ben, word_meaning)'''

s = s.replace(target_service, replacement_service)
with open(filepath_service, 'w') as f:
    f.write(s)
print("Python logic updated!")
