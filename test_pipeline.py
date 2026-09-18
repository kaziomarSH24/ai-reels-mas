import sys
sys.path.append('python_engine')
import os
from transformers import pipeline

idiom_model_path = "/var/www/python_engine/models/idiom_phrase_model"

cefr_classifier = pipeline(
    "token-classification", 
    model=idiom_model_path, 
    tokenizer=idiom_model_path,
)

texts = [
    "I have to take a rain check on that piece of cake.",
    "This is a normal sentence."
]
for t in texts:
    print(cefr_classifier(t))
