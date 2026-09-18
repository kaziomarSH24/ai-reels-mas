import os

filepath = 'python_engine/app/services/video_service.py'
with open(filepath, 'r') as f:
    content = f.read()

# Replace Gemini Prompt
old_gemini = '''    def _get_gemini_shortened_text(self, target: str, eng: str, ben: str):
        from app.services.ai_service import ai_agent
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return eng, ben, ""
            
        import requests
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
        
        prompt = f"""You are an EdTech video reel creator.
I have a movie dialogue: "{eng}"
The Bengali translation is: "{ben}"
The target Idiom or Hard Word is: "{target}"

I need to display this on a vertical 9:16 video reel. Space is VERY limited.
Please do 3 things:
1. Simplify the English sentence (max 10 words). Keep the target word/idiom in it!
2. Simplify the Bengali translation (max 10 words).
3. Provide a very short meaning (2-3 words) of the target word/idiom in English.

Return exactly 3 lines, nothing else:
Line 1: <simplified english>
Line 2: <simplified bengali>
Line 3: <short english meaning of target>
"""
        
        data = {
            "contents": [{"parts":[{"text": prompt}]}]
        }
        
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                result = response.json()
                text = result['candidates'][0]['content']['parts'][0]['text'].strip()
                lines = text.split('\n')
                if len(lines) >= 3:
                    return lines[0].replace('Line 1:','').strip(), lines[1].replace('Line 2:','').strip(), lines[2].replace('Line 3:','').strip()
            return eng[:50], ben[:50], ""
        except:
            pass
            
        return eng[:50], ben[:50], ""'''

new_gemini = '''    def _get_gemini_shortened_text(self, target: str, eng: str, ben: str):
        from app.services.ai_service import ai_agent
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return eng, ben, ""
            
        import requests
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
        
        prompt = f"""You are an English-to-Bengali vocabulary dictionary.
I have the phrase: "{target}"
Context dialogue: "{eng}"
Bengali dialogue: "{ben}"

Return ONLY the direct dictionary meaning of "{target}" in Bengali.
Keep it extremely short (max 2-3 words). 
Example: "খুব সহজ", "বিপাকে পড়া", "যোগাযোগ".
Return nothing else."""
        
        data = {
            "contents": [{"parts":[{"text": prompt}]}]
        }
        
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                result = response.json()
                text = result['candidates'][0]['content']['parts'][0]['text'].strip()
                # Return empty string for eng/ben so we don't display them anymore
                return "", "", text
            return "", "", ""
        except:
            pass
            
        return "", "", ""'''

content = content.replace(old_gemini, new_gemini)

# Replace the text overlay drawing
old_drawing = '''            # 1. Top Text
            target_display = target.upper()
            if word_meaning:
                target_display = f"{target.upper()} - {word_meaning}"
                
            y = 200
            y = draw_rounded_text([target_display], font_word, y, text_color=(0,0,0,255), bg_color=(255,215,0,255))
            
            t_words = [target]
            # 2. English Text
            y = 600
            lines_eng = wrap_text(short_eng, font_eng, 900)
            y = draw_rounded_text(lines_eng, font_eng, y, text_color=(255,255,255,255), bg_color=(0,0,0,180), target_words=t_words, highlight_color=(255,215,0,255))
            
            # 3. Bengali Text
            y = 1200
            lines_ben = wrap_text(short_ben, font_ben, 900)
            y = draw_rounded_text(lines_ben, font_ben, y, text_color=(150,255,150,255), bg_color=(0,0,0,180))'''

new_drawing = '''            # 1. Target Idiom (Huge Yellow Highlight)
            y = 300
            target_display = target.upper()
            y = draw_rounded_text([target_display], font_word, y, text_color=(0,0,0,255), bg_color=(255,215,0,255))
            
            # 2. Bengali Meaning (Huge Green Highlight)
            if word_meaning:
                y = 1300
                lines_ben = wrap_text(word_meaning, font_ben, 900)
                draw_rounded_text(lines_ben, font_ben, y, text_color=(255,255,255,255), bg_color=(0,150,0,200))'''

content = content.replace(old_drawing, new_drawing)

with open(filepath, 'w') as f:
    f.write(content)

print("Patch applied successfully!")
