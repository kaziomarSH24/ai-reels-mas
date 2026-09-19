import whisper
import os

class WhisperService:
    def __init__(self):
        print("[Whisper] Booting up Whisper Tiny model for micro-syncing...")
        # Load the Tiny model, which is extremely fast and lightweight
        self.model = whisper.load_model("tiny")

    def get_exact_timestamps(self, audio_chunk_path, target_expression):
        """
        Takes a small audio chunk (e.g., 5-10 seconds) and the target expression.
        Returns the exact start and end millisecond timestamps of that specific phrase.
        """
        print(f"[Whisper] Processing audio chunk for exact timestamps of: '{target_expression}'")

        try:
            # Transcribe with word-level timestamps enabled
            result = self.model.transcribe(audio_chunk_path, word_timestamps=True)
            
            # Default fallback timings if exact match fails
            exact_start = 0.0
            exact_end = 5.0

            words_data = []
            for segment in result['segments']:
                for word in segment['words']:
                    words_data.append({
                        "word": word['word'].strip().lower(),
                        "start": word['start'],
                        "end": word['end']
                    })

            # Clean and split the target expression to match against Whisper's output
            target_words = target_expression.lower().replace("'", "").replace(".", "").replace(",", "").split()
            
            if not target_words:
                return exact_start, exact_end

            # Search for the starting word of the expression in the transcription
            for i, w in enumerate(words_data):
                clean_whisper_word = w['word'].replace("'", "").replace(".", "").replace(",", "")
                
                if target_words[0] in clean_whisper_word:
                    exact_start = w['start']
                    
                    # Calculate the index of the final word in the expression
                    end_idx = min(i + len(target_words) - 1, len(words_data) - 1)
                    exact_end = words_data[end_idx]['end']
                    
                    # Add a 0.2s padding for natural audio cut
                    exact_start = max(0.0, exact_start - 0.2)
                    exact_end = exact_end + 0.2
                    break

            print(f"[Whisper] Micro-Sync Complete -> Start: {exact_start}s | End: {exact_end}s")
            return exact_start, exact_end

        except Exception as e:
            print(f"[Whisper] Error during micro-syncing: {e}")
            return 0.0, 5.0
