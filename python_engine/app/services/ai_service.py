import os
import warnings
from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
from dotenv import load_dotenv

load_dotenv('/var/www/.env')
warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

class AIService:
    _instance = None
    
    def __new__(cls):
        """
        Singleton pattern to ensure models are only loaded once into memory
        across all API requests.
        """
        if cls._instance is None:
            cls._instance = super(AIService, cls).__new__(cls)
            cls._instance._initialize_models()
        return cls._instance
        
    def _initialize_models(self):
        """
        Loads all required machine learning models into RAM during server boot.
        This eliminates the delay of disk I/O on every API request.
        """
        print("[AIService] Booting up AI Agents...")
        
        # Adjust path to reach the root 'python_engine' folder from 'app/services'
        script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # 1. Load Emotion Model
        print("Loading Emotion Model...")
        emotion_model_path = os.path.join(script_dir, "models", "emotion_model")
        self.emotion_classifier = pipeline(
            "text-classification", 
            model=emotion_model_path, 
            tokenizer=emotion_model_path
        )
        print("Emotion Model Ready!")
        
        # 2. Load Translation Model
        print("Loading Translation Model...")
        translation_model_name = "csebuetnlp/banglat5_nmt_en_bn"
        self.translation_tokenizer = AutoTokenizer.from_pretrained(translation_model_name, use_fast=False)
        self.translation_model = AutoModelForSeq2SeqLM.from_pretrained(translation_model_name)
        print("Translation Model Ready!")

        # 3. Load CEFR Difficulty Model
        print("Loading CEFR Difficulty Model...")
        cefr_model_path = os.path.join(script_dir, "models", "cefr_model")
        self.cefr_classifier = pipeline(
            "text-classification", 
            model=cefr_model_path, 
            tokenizer=cefr_model_path
        )
        print("CEFR Difficulty Model Ready!")

    def _translate_with_gemini(self, text: str, model_name: str) -> str:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment.")
            
        import requests
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        
        prompt = f"Translate the following English movie dialogue into casual, natural, and conversational Bengali. Provide ONLY the Bengali translation, nothing else. Dialogue: '{text}'"
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.3}
        }
        
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        return data['candidates'][0]['content']['parts'][0]['text'].strip()

    def analyze_dialogue(self, text: str):
        """
        Executes Emotion, CEFR, and Translation models concurrently on the input text.
        Returns a standardized dictionary containing the analysis payload.
        """
        # Analyze Emotion
        emotion_result = self.emotion_classifier(text)[0]
        emotion_conf = round(emotion_result['score'] * 100, 2)

        # Analyze CEFR Difficulty
        cefr_result = self.cefr_classifier(text)[0]
        cefr_lvl = cefr_result['label'].upper()
        cefr_conf = round(cefr_result['score'] * 100, 2)
        
        translation_result = ""
        success = False
        
        # SMART OPTIMIZATION: Only use Gemini for Hard (B2, C1, C2) sentences.
        # This prevents 429 Too Many Requests errors (15 RPM limit) for 10-minute videos.
        if cefr_lvl in ['B2', 'C1', 'C2']:
            gemini_models = ["gemini-3.8-flash", "gemini-3.6-flash", "gemini-3.5-flash"]
            for model in gemini_models:
                try:
                    translation_result = self._translate_with_gemini(text, model)
                    success = True
                    print(f"[AIService] Successfully translated using {model}")
                    break
                except Exception as e:
                    error_msg = str(e)
                    print(f"[AIService] {model} failed: {error_msg}")
                    # If quota exceeded, no point trying other Gemini models
                    if "429" in error_msg or "Too Many Requests" in error_msg:
                        print("[AIService] Gemini Quota Exceeded (429). Bypassing remaining Gemini models.")
                        break
                    import time
                    time.sleep(0.5)
                
        # Fallback to Local BanglaT5 for Easy sentences (A1, A2, B1) or if Gemini failed
        if not success:
            if cefr_lvl not in ['B2', 'C1', 'C2']:
                pass # Expected behavior for easy sentences
            else:
                print("[AIService] Gemini failed for hard sentence. Falling back to local BanglaT5 model.")
            
            inputs = self.translation_tokenizer(text, return_tensors="pt")
            generated_tokens = self.translation_model.generate(**inputs, max_length=100)
            translation_result = self.translation_tokenizer.decode(generated_tokens[0], skip_special_tokens=True)
        
        return {
            "emotion": emotion_result['label'].upper(),
            "emotion_confidence": emotion_conf,
            "cefr_level": cefr_lvl,
            "cefr_confidence": cefr_conf,
            "translation": translation_result
        }

# Global singleton instance for the FastAPI application
ai_agent = AIService()
