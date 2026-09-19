import google.generativeai as genai
import json

class GeminiService:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-3.5-flash-lite')

    def extract_all_vocabulary(self, vtt_content):
        print("[Gemini] Analyzing subtitles to extract ALL premium vocabulary...")

        prompt_instruction = """
        You are an expert English-to-Bengali linguistic AI.
        Analyze the following VTT subtitle text carefully. 
        Extract ALL highly useful, advanced English expressions, idioms, and smart words (e.g., "seconded", "I'm losing my nerve", "Chop chop") found in the text. Do not limit the count—extract as many as available.

        For each extracted item, provide:
        1. "expression": The exact spoken English idiom or word (e.g., "seconded", "avid").
        2. "type": Classify it as either "IDIOM", "PHRASAL_VERB", or "ADVANCED_WORD".
        3. "dictionary_meaning": The direct dictionary meaning in Bengali wrapped in parentheses (e.g., "(অর্থ: সমর্থন করা)").
        4. "original_sentence": The FULL, grammatically complete English sentence. If the sentence is split across multiple timestamp chunks, you MUST merge the chunks together into one complete sentence. NEVER output a half-finished or cut-off sentence.
        5. "sentence_translation": The accurate contextual Bengali translation of the FULL complete sentence.
        6. "rough_start": The start timestamp (in seconds) of the expression.
        7. "rough_end": The end timestamp (in seconds) of the expression.

        RETURN ONLY A VALID JSON ARRAY. NO MARKDOWN, NO EXTRA TEXT.
        Example Output Format:
        [
            {
                "expression": "seconded",
                "type": "ADVANCED_WORD",
                "dictionary_meaning": "(অর্থ: সমর্থন করা / দ্বিতীয় ব্যক্তি হিসেবে মত দেওয়া)",
                "original_sentence": "Yeah, seconded, it just gets a little cluttered.",
                "sentence_translation": "হ্যাঁ, আমিও একমত, এটা একটু বেশি ঘিঞ্জি হয়ে যায়।",
                "rough_start": 106.5,
                "rough_end": 109.0
            }
        ]

        Subtitle Data:
        """
        
        final_prompt = prompt_instruction + "\n" + vtt_content

        try:
            response = self.model.generate_content(
                final_prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json"
                )
            )
            
            clean_json = response.text.strip()
            vocabulary_list = json.loads(clean_json)
            
            print(f"[Gemini] Successfully extracted {len(vocabulary_list)} expressions!")
            return vocabulary_list

        except Exception as e:
            print(f"[Gemini] Error during extraction: {e}")
            return []
