import re

filepath = 'python_engine/app/services/video_service.py'
with open(filepath, 'r') as f:
    content = f.read()

# 1. Replace _get_gemini_shortened_text entirely
pattern = r'    def _get_gemini_shortened_text\(self, target: str, eng: str, ben: str\):.*?return eng\[:50\], ben\[:50\], ""'
replacement = '''    def _get_gemini_shortened_text(self, target: str, eng: str, ben: str):
        import os, requests
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key: return "", "", ""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        prompt = f"""You are an English-to-Bengali vocabulary dictionary.
I have the phrase: "{target}"
Context dialogue: "{eng}"
Bengali dialogue: "{ben}"

Return ONLY the direct dictionary meaning of "{target}" in Bengali.
Keep it extremely short (max 2-3 words). 
Example: "খুব সহজ", "বিপাকে পড়া", "যোগাযোগ".
Return nothing else."""
        try:
            r = requests.post(url, json={"contents": [{"parts":[{"text": prompt}]}]})
            if r.status_code == 200:
                t = r.json()['candidates'][0]['content']['parts'][0]['text'].strip()
                return "", "", t
        except: pass
        return "", "", ""'''
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# 2. Replace PIL drawing logic
pattern2 = r'# 1\. Top Text.*?y = draw_rounded_text\(ben_lines, font_ben, y, text_color=\(100,255,100,255\), bg_color=\(0,0,0,200\)\)'
replacement2 = '''# 1. Target Idiom (Huge Yellow Highlight)
            y = 300
            target_display = target.upper()
            y = draw_rounded_text([target_display], font_word, y, text_color=(0,0,0,255), bg_color=(255,215,0,255))
            
            # 2. Bengali Meaning (Huge Green Highlight)
            if word_meaning:
                y = 1300
                lines_ben = wrap_text(word_meaning, font_ben, 900)
                draw_rounded_text(lines_ben, font_ben, y, text_color=(255,255,255,255), bg_color=(0,150,0,200))'''
content = re.sub(pattern2, replacement2, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)
print("Regex patch applied!")
