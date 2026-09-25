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

    def fetch_and_parse(self, video_url: str, source_type: str = 'youtube') -> List[Dict]:
        """
        Fetches and parses subtitles.
        If youtube: uses yt-dlp.
        If gdrive/direct: uses ffmpeg to extract embedded SRT remotely without downloading the file.
        """
        import json
        import subprocess
        import webvtt
        
        # Use a hash of the URL as a cache ID
        import hashlib
        cache_id = hashlib.md5(video_url.encode()).hexdigest()
        if source_type == 'youtube':
            cache_id = self.extract_video_id(video_url) or cache_id
            
        cache_dir = '/var/www/storage/app/transcripts'
        os.makedirs(cache_dir, exist_ok=True)
        cache_file = os.path.join(cache_dir, f"{cache_id}.json")
        
        if os.path.exists(cache_file):
            print(f"[SubtitleService] Cache HIT for {cache_id}. Loading from local storage!")
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        print(f"[SubtitleService] Cache MISS. Fetching transcripts for: {video_url} ({source_type})")

        try:
            sub_file_path = f"/tmp/{cache_id}.srt"
            
            if source_type == 'youtube':
                cookie_path = '/var/www/storage/app/private/cookies.txt'
                sub_file = f"/tmp/{cache_id}"
                
                cmd = [
                    "yt-dlp",
                    "--write-auto-subs",
                    "--write-subs",
                    "--sub-lang", "en",
                    "--skip-download",
                    "-o", sub_file,
                    video_url
                ]
                
                if os.path.exists(cookie_path):
                    cmd.extend(["--cookies", cookie_path])
                    
                print(f"[SubtitleService] Running yt-dlp: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    raise Exception(f"yt-dlp failed: {result.stderr}")
                    
                vtt_path = f"{sub_file}.en.vtt"
                if not os.path.exists(vtt_path):
                    raise Exception("Subtitle file not found. Does the video have English subtitles?")
                    
                # Parse VTT
                captions = webvtt.read(vtt_path)
                transcript = []
                
                def timestamp_to_seconds(ts):
                    h, m, s = ts.split(':')
                    return int(h) * 3600 + int(m) * 60 + float(s)
                    
                for caption in captions:
                    text = caption.text.strip()
                    text = re.sub(r'<[^>]+>', '', text)
                    lines = text.split('\n')
                    unique_lines = []
                    for line in lines:
                        line = line.strip()
                        if line and line not in unique_lines:
                            unique_lines.append(line)
                    
                    text = ' '.join(unique_lines).strip()
                    if not text: continue
                        
                    start = timestamp_to_seconds(caption.start)
                    end = timestamp_to_seconds(caption.end)
                    
                    class Item:
                        def __init__(self, t, s, d):
                            self.text = t
                            self.start = s
                            self.duration = d
                            
                    transcript.append(Item(text, start, end - start))
                    
                os.remove(vtt_path)
                
            else:
                # GDrive or Direct URL: Extract true stream URL first using yt-dlp -g
                print(f"[SubtitleService] Resolving direct stream URL for {video_url}...")
                
                # We use --cookies here as well just in case the Drive link requires auth
                stream_cmd = ["yt-dlp", "-g", video_url]
                cookie_path = '/var/www/storage/app/private/cookies.txt'
                if os.path.exists(cookie_path):
                    stream_cmd.extend(["--cookies", cookie_path])
                    
                stream_result = subprocess.run(stream_cmd, capture_output=True, text=True)
                
                if stream_result.returncode != 0:
                    raise Exception(f"Failed to resolve stream URL with yt-dlp: {stream_result.stderr}")
                    
                stream_url = stream_result.stdout.strip().split('\n')[0] # Get the first stream URL
                
                if not stream_url.startswith('http'):
                    raise Exception(f"Invalid stream URL resolved: {stream_url}")
                    
                print("[SubtitleService] Extracting embedded subtitles directly via FFmpeg...")
                
                cmd = [
                    "ffmpeg", "-y", 
                    "-i", stream_url, 
                    "-map", "0:s:0?", # Map the first subtitle stream (if exists)
                    "-c:s", "srt",
                    "-f", "srt", 
                    sub_file_path
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if not os.path.exists(sub_file_path) or os.path.getsize(sub_file_path) == 0:
                    raise Exception(f"No subtitle stream found in the video. FFmpeg Error: {result.stderr}")
                    
                # Parse SRT
                import pysrt
                subs = pysrt.open(sub_file_path)
                transcript = []
                
                for sub in subs:
                    text = sub.text.replace('\n', ' ').strip()
                    text = re.sub(r'<[^>]+>', '', text) # Remove HTML tags in SRT if any
                    if not text: continue
                    
                    start_sec = sub.start.hours * 3600 + sub.start.minutes * 60 + sub.start.seconds + sub.start.milliseconds / 1000.0
                    end_sec = sub.end.hours * 3600 + sub.end.minutes * 60 + sub.end.seconds + sub.end.milliseconds / 1000.0
                    
                    class Item:
                        def __init__(self, t, s, d):
                            self.text = t
                            self.start = s
                            self.duration = d
                            
                    transcript.append(Item(text, start_sec, end_sec - start_sec))
                    
                os.remove(sub_file_path)
            
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
                            "start_sec": current_start,
                            "end_time": self.format_time(current_end),
                            "end_sec": current_end,
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
                            "start_sec": current_start,
                            "end_time": self.format_time(current_end),
                            "end_sec": current_end,
                            "text": current_text
                        })
                        current_text = ""
                        current_start = None
                        current_end = None

            if current_text:
                aggregated_dialogues.append({
                    "start_time": self.format_time(current_start),
                            "start_sec": current_start,
                    "end_time": self.format_time(current_end),
                            "end_sec": current_end,
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
