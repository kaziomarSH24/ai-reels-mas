import os
import warnings
from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer

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

    def analyze_dialogue(self, text: str):
        """
        Executes Emotion, CEFR, and Translation models concurrently on the input text.
        Returns a standardized dictionary containing the analysis payload.
        """
        # Analyze Emotion
        emotion_result = self.emotion_classifier(text)[0]

        # Analyze CEFR Difficulty
        cefr_result = self.cefr_classifier(text)[0]
        
        # Translate to Bangla
        inputs = self.translation_tokenizer(text, return_tensors="pt")
        generated_tokens = self.translation_model.generate(**inputs, max_length=100)
        translation_result = self.translation_tokenizer.decode(generated_tokens[0], skip_special_tokens=True)
        
        return {
            "emotion": emotion_result['label'].upper(),
            "confidence": round(emotion_result['score'] * 100, 2),
            "cefr_level": cefr_result['label'].upper(),
            "translation": translation_result
        }

# Global singleton instance for the FastAPI application
ai_agent = AIService()
