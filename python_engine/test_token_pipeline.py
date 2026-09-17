from transformers import pipeline
import os

model_path = "models/word_level_cefr_model"
if not os.path.exists(model_path):
    print("Model not found at", model_path)
    exit()

print("Loading pipeline...")
cefr_classifier = pipeline("token-classification", model=model_path, tokenizer=model_path, aggregation_strategy="simple")

text = "That was a magnificent and ephemeral performance."
results = cefr_classifier(text)
print("Results:", results)
