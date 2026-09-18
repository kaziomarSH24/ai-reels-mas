import re
filepath = 'python_engine/app/services/video_service.py'
with open(filepath, 'r') as f:
    content = f.read()

target = '''        print(f"[VideoService] Generating Compilation Reel with {len(clips)} clips using Whisper AI...")
        processed_files = []'''

replacement = '''        print(f"[VideoService] Generating Compilation Reel with {len(clips)} clips using Whisper AI...")
        processed_files = []
        gemini_cache = {}'''
content = content.replace(target, replacement)

target2 = '''            # --- GEMINI EXTRACTION ---
            eng_text = str(clip.get('english_text', '')).strip()
            ben_text = str(clip.get('bengali_text', '')).strip()
            
            short_eng, short_ben, word_meaning = self._get_gemini_shortened_text(target, eng_text, ben_text)'''

replacement2 = '''            # --- GEMINI EXTRACTION ---
            eng_text = str(clip.get('english_text', '')).strip()
            ben_text = str(clip.get('bengali_text', '')).strip()
            
            if target in gemini_cache:
                short_eng, short_ben, word_meaning = gemini_cache[target]
            else:
                short_eng, short_ben, word_meaning = self._get_gemini_shortened_text(target, eng_text, ben_text)
                gemini_cache[target] = (short_eng, short_ben, word_meaning)'''

content = content.replace(target2, replacement2)

with open(filepath, 'w') as f:
    f.write(content)
print("Caching implemented!")
