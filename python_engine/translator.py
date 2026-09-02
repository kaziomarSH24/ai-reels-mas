from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import sys
import warnings
import torch

# Suppress HuggingFace warnings for cleaner output
warnings.filterwarnings("ignore")

def translate_en_to_bn(text):
    print("🤖 Loading BUET NLP Translation Model...")
    print(f"🎯 Device: {'GPU' if torch.cuda.is_available() else 'CPU'}")
    
    # We use banglat5_nmt_en_bn from BUET NLP which is specifically fine-tuned for EN to BN
    model_name = "csebuetnlp/banglat5_nmt_en_bn"
    
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    
    print(f"\n🇬🇧 English: '{text}'")
    
    # Process the text
    input_ids = tokenizer(text, return_tensors="pt").input_ids
    generated_tokens = model.generate(input_ids)
    decoded_translation = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
    
    print(f"🇧🇩 Bengali: '{decoded_translation}'\n")
    return decoded_translation

if __name__ == "__main__":
    # Test with a default sentence, or take input from terminal
    test_sentence = "I am very happy to start this AI thesis project."
    
    if len(sys.argv) > 1:
        test_sentence = sys.argv[1]
        
    translate_en_to_bn(test_sentence)
