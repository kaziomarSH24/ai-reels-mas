from transformers import pipeline

model_path = "./models/idiom_phrase_model"
try:
    print(f"Loading model from {model_path}...")
    nlp = pipeline("ner", model=model_path, tokenizer=model_path)
    
    text = "To be honest, it is a piece of cake for him, but I do not want to have egg on my face."
    print(f"Testing on sentence: '{text}'")
    
    results = nlp(text)
    
    print("\n--- RESULTS ---")
    for r in results:
        # Ignore 'O' (Normal words) just to show the extracted idioms/hard words clearly
        if r['entity'] != 'O':
            print(f"Word: {r['word']:<10} | Tag: {r['entity']:<10} | Score: {r['score']:.4f}")
            
    print("\nModel is loaded and working correctly!")
except Exception as e:
    print(f"Error: {e}")
