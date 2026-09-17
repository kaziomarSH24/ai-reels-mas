with open("python_engine/app/services/video_service.py", "r") as f:
    content = f.read()

# Fix yt-dlp format command
old_yt_dlp = """            dl_cmd = [
                "yt-dlp",
                "--cookies", "/var/www/cookies.txt",
                "-f", "best",
                "--download-sections", f"*{dl_start}-{dl_end}",
                "--force-keyframes-at-cuts",
                "-o", raw_path,
                clip['source_url']
            ]"""

new_yt_dlp = """            dl_cmd = [
                "yt-dlp",
                "--cookies", "/var/www/cookies.txt",
                "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best",
                "--download-sections", f"*{dl_start}-{dl_end}",
                "--force-keyframes-at-cuts",
                "-o", raw_path,
                clip['source_url']
            ]"""

# Clean FFmpeg command (remove anullsrc and multiple maps)
old_ffmpeg = """            ffmpeg_cmd = [
                "ffmpeg", "-y",
                "-i", raw_path,
                "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
                "-vf", vf_filter,
                "-r", "30",
                "-c:v", "libx264",
                "-preset", "fast",
                "-c:a", "aac",
                "-ar", "44100",
                "-ac", "2",
                "-map", "0:v:0",
                "-map", "0:a:0?",
                "-map", "1:a:0",
                "-shortest",
                proc_path
            ]"""

new_ffmpeg = """            ffmpeg_cmd = [
                "ffmpeg", "-y",
                "-i", raw_path,
                "-vf", vf_filter,
                "-r", "30",
                "-c:v", "libx264",
                "-preset", "fast",
                "-c:a", "aac",
                "-ar", "44100",
                "-ac", "2",
                proc_path
            ]"""

content = content.replace(old_yt_dlp, new_yt_dlp).replace(old_ffmpeg, new_ffmpeg)

with open("python_engine/app/services/video_service.py", "w") as f:
    f.write(content)
