import re

with open("python_engine/app/services/subtitle_service.py", "r") as f:
    content = f.read()

new_logic = r"""
        try:
            import subprocess
            import webvtt
            
            cookie_path = '/var/www/cookies.txt'
            
            # Temporary file to save subtitle
            sub_file = f"/tmp/{video_id}"
            
            cmd = [
                "yt-dlp",
                "--write-auto-subs",
                "--write-subs",
                "--sub-lang", "en",
                "--skip-download",
                "-o", sub_file,
                youtube_url
            ]
            
            if os.path.exists(cookie_path):
                cmd.extend(["--cookies", cookie_path])
                print("[SubtitleService] Using cookies.txt for yt-dlp to bypass IP block.")
            else:
                print("[SubtitleService] WARNING: cookies.txt not found. IP might get blocked.")
                
            print(f"[SubtitleService] Running yt-dlp: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"[SubtitleService] yt-dlp Error: {result.stderr}")
                raise Exception(f"yt-dlp failed to download subtitles: {result.stderr}")
                
            # yt-dlp saves it as /tmp/{video_id}.en.vtt
            vtt_path = f"{sub_file}.en.vtt"
            if not os.path.exists(vtt_path):
                raise Exception(f"Subtitle file not found at {vtt_path}. Does the video have English subtitles?")
                
            captions = webvtt.read(vtt_path)
            
            def timestamp_to_seconds(ts):
                h, m, s = ts.split(':')
                return int(h) * 3600 + int(m) * 60 + float(s)
                
            transcript = []
            for caption in captions:
                text = caption.text.strip()
                # Clean yt-dlp auto-sub duplicate formatting
                text = re.sub(r'<[^>]+>', '', text)
                lines = text.split('\n')
                # Remove empty lines and duplicates preserving order
                unique_lines = []
                for line in lines:
                    line = line.strip()
                    if line and line not in unique_lines:
                        unique_lines.append(line)
                
                text = ' '.join(unique_lines).strip()
                if not text:
                    continue
                    
                start = timestamp_to_seconds(caption.start)
                end = timestamp_to_seconds(caption.end)
                
                class Item:
                    def __init__(self, t, s, d):
                        self.text = t
                        self.start = s
                        self.duration = d
                        
                transcript.append(Item(text, start, end - start))
                
            os.remove(vtt_path) # Cleanup
            
            aggregated_dialogues = []
            current_text = ""
            current_start = None
            current_end = None
            word_count = 0
            
            end_punctuations = re.compile(r'[.!?]$')
            
            for item in transcript:
                text = item.text
                start = item.start
                duration = item.duration
                end = start + duration
                
                clean_text = re.sub(r'\s+', ' ', text).strip()
                
                if len(clean_text) < 2 or (clean_text.startswith('[') and clean_text.endswith(']')):
                    continue

                if current_end is not None and (start - current_end) > 0.8:
                    if current_text:
                        aggregated_dialogues.append({
                            "start_time": self.format_time(current_start),
                            "end_time": self.format_time(current_end),
                            "text": current_text
                        })
                        current_text = ""
                        current_start = None
                        word_count = 0

                if current_start is None:
                    current_start = start
                
                if current_text:
                    current_text += " " + clean_text
                else:
                    current_text = clean_text
                    
                current_end = end
                
                chunk_duration = current_end - current_start
                word_count = len(current_text.split())
                
                if end_punctuations.search(clean_text) or chunk_duration >= 5.0 or word_count >= 12:
                    if chunk_duration >= 1.5 or end_punctuations.search(clean_text):
                        aggregated_dialogues.append({
                            "start_time": self.format_time(current_start),
                            "end_time": self.format_time(current_end),
                            "text": current_text
                        })
                        current_text = ""
                        current_start = None
                        current_end = None

            if current_text:
                aggregated_dialogues.append({
                    "start_time": self.format_time(current_start),
                    "end_time": self.format_time(current_end),
                    "text": current_text
                })

            print(f"[SubtitleService] Extracted {len(aggregated_dialogues)} clean dialogue segments.")
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(aggregated_dialogues, f, ensure_ascii=False, indent=4)
            print(f"[SubtitleService] Saved transcript to cache: {cache_file}")
            
            return aggregated_dialogues

        except Exception as e:
            print(f"Error fetching transcript: {e}")
            raise Exception(f"Failed to fetch subtitles: {str(e)}")
"""

content = re.sub(
    r"        try:\s*import http\.cookiejar[\s\S]*?raise Exception\(f\"Failed to fetch subtitles.*?\"\)",
    new_logic.strip().replace("\\", "\\\\"),
    content
)

with open("python_engine/app/services/subtitle_service.py", "w") as f:
    f.write(content)

