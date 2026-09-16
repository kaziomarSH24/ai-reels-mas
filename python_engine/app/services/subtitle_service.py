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
        Uses cookies.txt to bypass YouTube IP bans.
        """
        video_id = self.extract_video_id(youtube_url)
        if not video_id:
            raise Exception("Invalid YouTube URL.")

        try:
            print(f"[SubtitleService] Fetching transcripts for video ID: {video_id}")
            
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
                
                # Clean text (remove newlines from within the same subtitle block)
                clean_text = re.sub(r'\s+', ' ', text).strip()
                
                if len(clean_text) < 2 or (clean_text.startswith('[') and clean_text.endswith(']')):
                    continue # Skip sounds like [Music] or [Applause]

                if current_start is None:
                    current_start = start
                
                if current_text:
                    current_text += " " + clean_text
                else:
                    current_text = clean_text
                    
                current_end = end
                word_count = len(current_text.split())
                
                if end_punctuations.search(clean_text) or word_count >= 5:
                    aggregated_dialogues.append({
                        "start_time": self.format_time(current_start),
                        "end_time": self.format_time(current_end),
                        "text": current_text
                    })
                    current_text = ""
                    current_start = None
                    current_end = None
                    word_count = 0

            if current_text:
                aggregated_dialogues.append({
                    "start_time": self.format_time(current_start),
                    "end_time": self.format_time(current_end),
                    "text": current_text
                })

            print(f"[SubtitleService] Extracted {len(aggregated_dialogues)} clean dialogue segments.")
            return aggregated_dialogues

        except Exception as e:
            print(f"Error fetching transcript: {e}")
            raise Exception(f"Failed to fetch subtitles. Make sure the video has CC enabled. Error: {str(e)}")
