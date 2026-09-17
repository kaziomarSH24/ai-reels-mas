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
        if cls._instance is None:
            cls._instance = super(AIService, cls).__new__(cls)
            cls._instance._initialize_models()
        return cls._instance
        
    def _initialize_models(self):
        print("[AIService] Booting up AI Agents...")
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

        # 3. Load Multi-Entity Model (Idioms + Hard Words)
        print("Loading Idiom/Phrase Model...")
        idiom_model_path = os.path.join(script_dir, "models", "idiom_phrase_model")
        self.cefr_classifier = pipeline(
            "token-classification", 
            model=idiom_model_path, 
            tokenizer=idiom_model_path,
            aggregation_strategy="simple"
        )
        print("Idiom/Phrase Model Ready!")
        
        self.stop_words = {'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at', 'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she', 'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know', 'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us', 'are', 'is', 'was', 'were', 'am', 'been', 'being', 'has', 'had', 'did', 'done', 'doing', 'does', 'down', 'very', 'really', 'world', 'here', 'where', 'why', 'much', 'many', 'lot', 'little', 'few', 'big', 'small', 'large', 'long', 'short', 'old', 'young', 's', 't', 'm', 're', 've', 'll', 'd', 'just', 'going', 'gonna', 'wanna'}

    def is_valid_target(self, word):
        word = word.lower().strip()
        words = word.split()
        
        if len(words) == 1:
            if len(word) < 6: return False
            if word in self.stop_words: return False
            return True
            
        if len(words) > 4: return False
        
        all_stop = True
        for w in words:
            if w not in self.stop_words:
                all_stop = False
                break
                
        if all_stop:
            return False
            
        return True

    def batch_analyze_dialogues(self, texts: list[str]):
        results = []
        print(f"[AIService] Running Fast Local AI for {len(texts)} dialogues...")
        
        for text in texts:
            emotion_res = self.emotion_classifier(text)[0]
            tokens = self.cefr_classifier(text)
            
            target_word = "None"
            highest_level = "NORMAL"
            confidence = 1.0
            
            best_token = None
            for token in tokens:
                lbl = token['entity_group']
                word_clean = token['word'].strip()
                
                # Confidence Filter
                score = float(token['score'])
                if lbl == 'IDIOM' and score < 0.50:
                    continue
                elif lbl == 'HARD_WORD' and score < 0.70:
                    continue
                    
                # Intelligent Overfit Filter
                if not self.is_valid_target(word_clean):
                    continue
                    
                if lbl in ['IDIOM', 'HARD_WORD']:
                    if best_token is None:
                        best_token = token
                    else:
                        if best_token['entity_group'] == 'HARD_WORD' and lbl == 'IDIOM':
                            best_token = token
                        elif best_token['entity_group'] == lbl and len(word_clean) > len(best_token['word'].strip()):
                            best_token = token

            if best_token:
                target_word = best_token['word'].strip()
                highest_level = best_token['entity_group']
                confidence = float(best_token['score'])
            
            bn_translation = "Will translate during reel generation..."

            results.append({
                "text": text,
                "emotion": emotion_res['label'].upper(),
                "emotion_confidence": round(emotion_res['score'] * 100, 2),
                "cefr_level": highest_level,
                "cefr_confidence": round(confidence * 100, 2),
                "target_word": target_word,
                "translation": bn_translation, 
                "fixed_english": text 
            })
            
        return results

ai_agent = AIService()
