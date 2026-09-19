import os
from dotenv import load_dotenv
load_dotenv('/var/www/.env')
import google.generativeai as genai
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-3.5-flash-lite')

vtt = """
40.00 --> 42.50
They help us connect the dots and realize that what we eat
42.50 --> 45.00
has a direct impact on our health.
"""

prompt = """
You are an expert English-to-Bengali linguistic AI.
Analyze the following VTT subtitle text carefully. 
Extract ALL highly useful, advanced English expressions, idioms, and smart words (e.g., "seconded", "I'm losing my nerve", "Chop chop") found in the text. Do not limit the count—extract as many as available.

For each extracted item, provide:
1. "expression": The exact spoken English idiom or word (e.g., "seconded", "avid").
2. "type": Classify it as either "IDIOM", "PHRASAL_VERB", or "ADVANCED_WORD".
3. "dictionary_meaning": The direct dictionary meaning in Bengali wrapped in parentheses (e.g., "(অর্থ: সমর্থন করা)").
4. "original_sentence": The full complete spoken sentence where it was used.
5. "sentence_translation": The accurate contextual Bengali translation of the full sentence.
6. "rough_start": The start timestamp (in seconds).
7. "rough_end": The end timestamp (in seconds).

RETURN ONLY A VALID JSON ARRAY. NO MARKDOWN, NO EXTRA TEXT.
Subtitle Data:
""" + vtt

print(model.generate_content(prompt).text)
