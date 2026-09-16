import os
import subprocess
from datetime import datetime

class VideoService:
    def __init__(self):
        self.tmp_dir = "/tmp/snapclip/reels"
        self.output_dir = "/var/www/public/generated_reels"
        os.makedirs(self.tmp_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

    def _time_to_seconds(self, time_str: str) -> float:
        """Converts HH:MM:SS.mmm to seconds"""
        h, m, s = time_str.split(':')
        return int(h) * 3600 + int(m) * 60 + float(s)

    def extract_and_crop_clip(self, source_url: str, start_time: str, duration: int, output_filename: str, english_text: str, bengali_text: str) -> str:
        """
        Downloads a specific segment from YouTube using yt-dlp (with cookies),
        crops it to 9:16 vertical format, and overlays Alex Hormozi style text.
        """
        # Calculate end time in seconds (for yt-dlp)
        start_sec = self._time_to_seconds(start_time)
        end_sec = start_sec + duration

        # Add 1 second padding for smooth transition
        dl_start = max(0, start_sec - 1)
        dl_end = end_sec + 1

        raw_video_path = os.path.join(self.tmp_dir, f"raw_{output_filename}")
        final_video_path = os.path.join(self.output_dir, output_filename)

        print(f"[VideoService] Downloading section from {dl_start} to {dl_end} for {source_url}")

        # Download specifically the section using yt-dlp 
        # CRITICAL: Must use [vcodec^=avc] (H.264) because VP9/DASH fails on exact section extraction in ffmpeg!
        dl_cmd = [
            "yt-dlp",
            "--cookies", "/var/www/cookies.txt",
            "-f", "bestvideo[ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]/mp4",
            "--download-sections", f"*{dl_start}-{dl_end}",
            "--force-keyframes-at-cuts",
            "-o", raw_video_path,
            source_url
        ]
        
        dl_process = subprocess.run(dl_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if not os.path.exists(raw_video_path):
            print(dl_process.stderr)
            raise Exception("Failed to download video section. It might be private or cookies expired.")

        import textwrap
        
        print(f"[VideoService] Processing and Cropping to 9:16 vertical with Subtitles...")
        
        # Fix: Wrap text so it doesn't go out of the screen (max 20 characters per line)
        wrapped_eng = textwrap.fill(english_text.strip(), width=25)
        wrapped_ben = textwrap.fill(bengali_text.strip(), width=25)
        
        # Write text to files to avoid FFmpeg escaping hell
        eng_txt_path = os.path.join(self.tmp_dir, f"eng_{output_filename}.txt")
        ben_txt_path = os.path.join(self.tmp_dir, f"ben_{output_filename}.txt")
        with open(eng_txt_path, "w", encoding="utf-8") as f:
            f.write(wrapped_eng)
        with open(ben_txt_path, "w", encoding="utf-8") as f:
            f.write(wrapped_ben)

        # FFmpeg command for Professional 9:16 cropping (Alex Hormozi style)
        # scale=-1:1920 (scales height to 1920, keeps aspect ratio for width)
        # crop=1080:1920 (crops the center 1080 pixels of the width)
        # drawtext (English at the top, Bengali at the bottom)
        font_path = "/tmp/HindSiliguri-Bold.ttf"
        
        # We use a solid background box or shadow to make text pop!
        vf_filter = (
            "scale=-1:1920,crop=1080:1920,"
            f"drawtext=fontfile='{font_path}':textfile='{eng_txt_path}':fontcolor=white:fontsize=80:x=(w-text_w)/2:y=(h/2)-200:box=1:boxcolor=black@0.6:boxborderw=20,"
            f"drawtext=fontfile='{font_path}':textfile='{ben_txt_path}':fontcolor=yellow:fontsize=70:x=(w-text_w)/2:y=(h/2)+100:box=1:boxcolor=black@0.6:boxborderw=20"
        )

        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-i", raw_video_path,
            "-vf", vf_filter,
            "-c:v", "libx264",
            "-preset", "fast",
            "-c:a", "aac",
            final_video_path
        ]

        ffmpeg_process = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if not os.path.exists(final_video_path):
            print(ffmpeg_process.stderr)
            raise Exception("FFmpeg failed to process the video.")

        # Cleanup
        try:
            os.remove(raw_video_path)
            os.remove(eng_txt_path)
            os.remove(ben_txt_path)
        except:
            pass

        return f"/generated_reels/{output_filename}"
