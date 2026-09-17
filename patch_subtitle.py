with open("python_engine/app/services/subtitle_service.py", "r") as f:
    content = f.read()

old_logic = """                # Break if it ends with punctuation, OR if the continuous speech exceeds 15 seconds
                chunk_duration = current_end - current_start
                if end_punctuations.search(clean_text) or chunk_duration >= 15.0:
                    aggregated_dialogues.append({
                        "start_time": self.format_time(current_start),
                        "end_time": self.format_time(current_end),
                        "text": current_text
                    })
                    current_text = ""
                    current_start = None
                    current_end = None"""

new_logic = """                # REEL GENERATION LOGIC: Break into short, punchy 3-5 second TikTok style clips.
                chunk_duration = current_end - current_start
                word_count = len(current_text.split())
                
                # Force break if punctuation, OR duration hits 5 seconds, OR word count > 12
                # Auto-generated subtitles have no punctuation, so we rely heavily on time/word limit.
                if end_punctuations.search(clean_text) or chunk_duration >= 5.0 or word_count >= 12:
                    # Ignore extremely short chunks (like a 0.5s "Yeah") unless it's the end of a thought
                    if chunk_duration >= 1.5 or end_punctuations.search(clean_text):
                        aggregated_dialogues.append({
                            "start_time": self.format_time(current_start),
                            "end_time": self.format_time(current_end),
                            "text": current_text
                        })
                        current_text = ""
                        current_start = None
                        current_end = None"""

content = content.replace(old_logic, new_logic)

with open("python_engine/app/services/subtitle_service.py", "w") as f:
    f.write(content)
