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
        Extract ALL highly useful, advanced English expressions, idioms, and smart daily conversational phrases (e.g., "I'm broke", "Connect the dots", "Inevitable"). Do not limit the count-extract as many as available. 
        CRITICAL RULE: Never rewrite a phrase into a completely different idiom. The extracted expression must be constructed ONLY from words actually spoken in the sentence (ignoring filler words).

        For each extracted item, provide exactly this JSON structure:
        1. "expression": The clean, base form of the word/idiom (e.g., "I'm broke" extracted from "I'm completely broke"). CRITICAL: The core words MUST exist in the spoken sentence. You may skip filler words (like "completely", "uh", "literally") to make a clean expression, but DO NOT substitute core words with synonyms (e.g., if they say "back then", DO NOT rewrite it as "back in the day").
        2. "whisper_target": The EXACT verbatim phrase spoken in the video including filler words (e.g., "I'm completely broke").
        3. "category": Classify strictly as "IDIOM", "ADVANCED_WORD", or "DAILY_PHRASE".
        4. "casual_meaning": Conversational, everyday Bengali meaning (not formal dictionary language).
        5. "original_sentence": The FULL, grammatically complete English sentence EXACTLY as spoken.
        6. "original_translation": Casual Bengali translation of the full original sentence.
        7. "easy_example": Create a highly practical, conversational, and relatable example sentence (4-7 words) using the expression. The context should feel natural to daily life (e.g., hanging out with friends, office talk, or casual chatting). Avoid robotic or textbook sentences. Make it sound like how native speakers actually talk.
        8. "example_translation": Bengali translation of the easy example.
        9. "start_id": Look at the [ID: X] tags. Return the integer ID where this sentence STARTS.
        10. "end_id": Return the integer ID where this sentence ENDS.

        RETURN ONLY A VALID JSON ARRAY. DO NOT WRAP THE RESPONSE IN MARKDOWN CODE BLOCKS (like ```json). JUST RAW JSON.

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
            "start_id": 14,
            "end_id": 16
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
            # Strip markdown blocks if the model ignores the instruction
            if clean_json.startswith("```json"):
                clean_json = clean_json[7:]
            if clean_json.startswith("```"):
                clean_json = clean_json[3:]
            if clean_json.endswith("```"):
                clean_json = clean_json[:-3]
            clean_json = clean_json.strip()
            
            vocabulary_list = json.loads(clean_json)
            
            print(f"[GeminiService] Successfully extracted {len(vocabulary_list)} expressions!")
            return vocabulary_list

        except Exception as e:
            print(f"[GeminiService] Error during extraction: {e}")
            return []
