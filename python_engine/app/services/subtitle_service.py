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
            import http.cookiejar
            from requests import Session
            
            # Load cookies to bypass Bot 429 Error
            cookie_path = '/var/www/cookies.txt'
            session = Session()
            if os.path.exists(cookie_path):
                cookie_jar = http.cookiejar.MozillaCookieJar(cookie_path)
                cookie_jar.load(ignore_discard=True, ignore_expires=True)
                session.cookies = cookie_jar
                print("[SubtitleService] Successfully loaded YouTube cookies.")
            else:
                print("[SubtitleService] WARNING: cookies.txt not found. IP might get blocked.")

            api = YouTubeTranscriptApi(http_client=session)
            transcript = api.fetch(video_id, languages=['en'])
            
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

                # If there's a pause (> 0.8s), force a break as it indicates a new thought
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
                
                # Break if it ends with punctuation, OR if the continuous speech exceeds 15 seconds
                chunk_duration = current_end - current_start
                if end_punctuations.search(clean_text) or chunk_duration >= 15.0:
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
            
            # Save to Cache
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(aggregated_dialogues, f, ensure_ascii=False, indent=4)
            print(f"[SubtitleService] Saved transcript to cache: {cache_file}")
            
            return aggregated_dialogues

        except Exception as e:
            print(f"Error fetching transcript: {e}")
            raise Exception(f"Failed to fetch subtitles. Make sure the video has CC enabled. Error: {str(e)}")
