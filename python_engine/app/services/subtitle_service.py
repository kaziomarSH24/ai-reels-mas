import os
import re
from typing import List, Dict
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

class SubtitleService:
    def __init__(self):
        pass

    def extract_video_id(self, youtube_url: str) -> str:
        """Extracts the video ID from a YouTube URL."""
        query = urlparse(youtube_url)
        if query.hostname == 'youtu.be':
            return query.path[1:]
        if query.hostname in ('www.youtube.com', 'youtube.com'):
            if query.path == '/watch':
                p = parse_qs(query.query)
                return p['v'][0]
            if query.path[:7] == '/embed/':
                return query.path.split('/')[2]
            if query.path[:3] == '/v/':
                return query.path.split('/')[2]
        return ""

    def format_time(self, seconds: float) -> str:
        """Converts seconds into HH:MM:SS.mmm format for FFmpeg compatibility."""
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return f"{int(h):02d}:{int(m):02d}:{s:06.3f}"

    def fetch_and_parse(self, youtube_url: str) -> List[Dict]:
        """
        Uses youtube-transcript-api to fetch clean subtitles instantly.
        Uses local caching to bypass IP blocks for previously fetched videos.
        """
        video_id = self.extract_video_id(youtube_url)
        if not video_id:
            raise Exception("Invalid YouTube URL.")

        # ==========================================
        # SMART SOLUTION: Caching Mechanism
        # ==========================================
        import json
        cache_dir = '/var/www/storage/app/transcripts'
        os.makedirs(cache_dir, exist_ok=True)
        cache_file = os.path.join(cache_dir, f"{video_id}.json")
        
        if os.path.exists(cache_file):
            print(f"[SubtitleService] Cache HIT for {video_id}. Loading from local storage!")
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        print(f"[SubtitleService] Cache MISS. Fetching transcripts for video ID: {video_id} from YouTube...")

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
