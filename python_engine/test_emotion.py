import sys
import warnings
from transformers import pipeline

# Ignore warnings for cleaner terminal output
warnings.filterwarnings("ignore")

print("🤖 Loading Custom Hunter Agent (Emotion Model)...")

try:
    # Load the local model we trained on Kaggle
    classifier = pipeline(
        "text-classification", 
        model="python_engine/models/emotion_model", 
        tokenizer="python_engine/models/emotion_model"
    )
    print("✅ Model loaded successfully from local storage!\n")
except Exception as e:
    print(f"❌ Failed to load model. Error: {e}")
    sys.exit(1)

# A list of movie dialogues to test
test_dialogues = [
    "I am completely fed up with your nonsense!", 
    "Out of the blue, he just showed up and I was shocked!",
    "I am so happy that our thesis project is working perfectly.",
    "I feel so lonely and depressed today without you."
]

print("🎯 Testing Dialogues:\n" + "-"*50)
for text in test_dialogues:
    result = classifier(text)[0]
    emotion = result['label'].upper()
    confidence = result['score'] * 100
    
    print(f"📝 Dialogue : '{text}'")
    print(f"🧠 Detected : {emotion} (Confidence: {confidence:.2f}%)\n")
