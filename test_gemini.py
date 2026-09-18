import os
import requests
from dotenv import load_dotenv
load_dotenv('/var/www/.env')

api_key = os.environ.get("GEMINI_API_KEY")
target = "piece of cake"
eng = "You can share a piece of cake..."
ben = ""

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
    result = response.json()
    text = result['candidates'][0]['content']['parts'][0]['text'].strip()
    print("Gemini Output:", text)
except Exception as e:
    print("Error:", str(e))
