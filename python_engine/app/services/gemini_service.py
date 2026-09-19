import google.generativeai as genai
import json

class GeminiService:
    """
    Handles interactions with the Google Gemini API to extract 
    linguistic data from VTT subtitles.
    """
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-3.5-flash-lite')

    def extract_all_vocabulary(self, vtt_content: str) -> list:
        """
        Extracts phrases, idioms, and advanced vocabulary from VTT chunks 
        and maps them to a highly structured JSON array.
        """
        print("[GeminiService] Analyzing subtitles to extract premium vocabulary...")

        prompt_instruction = """
        You are an expert English-to-Bengali linguistic AI.
        Analyze the following VTT subtitle text carefully. 
        Extract ALL highly useful, advanced English expressions, idioms, and smart daily conversational phrases (e.g., "I'm broke", "Connect the dots", "Inevitable"). Do not limit the count—extract as many as available. 
        CRITICAL RULE: Never rewrite a phrase into a completely different idiom. The extracted expression must be constructed ONLY from words actually spoken in the sentence (ignoring filler words).

        For each extracted item, provide exactly this JSON structure:
        1. "expression": The clean, base form of the word/idiom (e.g., "I'm broke" extracted from "I'm completely broke"). CRITICAL: The core words MUST exist in the spoken sentence. You may skip filler words (like "completely", "uh", "literally") to make a clean expression, but DO NOT substitute core words with synonyms (e.g., if they say "back then", DO NOT rewrite it as "back in the day").
        2. "whisper_target": The EXACT verbatim phrase spoken in the video including filler words (e.g., "I'm completely broke").
        3. "category": Classify strictly as "IDIOM", "ADVANCED_WORD", or "DAILY_PHRASE".
        4. "casual_meaning": Conversational, everyday Bengali meaning (not formal dictionary language).
        5. "original_sentence": The FULL, grammatically complete English sentence. Merge chunks if split across multiple timestamps.
        6. "original_translation": Casual Bengali translation of the full original sentence.
        7. "easy_example": Create a short, simple 3-5 word example sentence using the expression.
        8. "example_translation": Bengali translation of the easy example.
        9. "rough_start": The start timestamp (in seconds, float) of the sentence. IMPORTANT: If the sentence is merged from multiple chunks, take the start timestamp from the FIRST chunk.
        10. "rough_end": The end timestamp (in seconds, float) of the sentence. IMPORTANT: If the sentence is merged from multiple chunks, take the end timestamp from the LAST chunk.

        If a single sentence contains multiple hard words or idioms, output them as SEPARATE objects in the array.

        RETURN ONLY A VALID JSON ARRAY. NO MARKDOWN, NO EXTRA TEXT.
        Example Output Format:
        [
          {
            "expression": "I'm broke",
            "whisper_target": "I'm completely broke",
            "category": "DAILY_PHRASE",
            "casual_meaning": "পকেট ফাঁকা / টাকা-পয়সা না থাকা",
            "original_sentence": "I'd love to grab a coffee with you, but honestly, I'm completely broke right now.",
            "original_translation": "তোমার সাথে কফি খেতে ভালোই লাগতো, কিন্তু সত্যি বলতে, আমার পকেট এখন একদম ফাঁকা।",
            "easy_example": "I can't buy that shirt, I'm broke.",
            "example_translation": "আমি ওই শার্টটা কিনতে পারবো না, আমার কাছে টাকা নেই।",
            "rough_start": 40.50,
            "rough_end": 45.00
          }
        ]

        Subtitle Data:
        """
        
        final_prompt = f"{prompt_instruction}\n{vtt_content}"

        try:
            response = self.model.generate_content(
                final_prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json"
                )
            )
            
            clean_json = response.text.strip()
            vocabulary_list = json.loads(clean_json)
            
            print(f"[GeminiService] Successfully extracted {len(vocabulary_list)} expressions!")
            return vocabulary_list

        except Exception as e:
            print(f"[GeminiService] Error during extraction: {e}")
            return []
