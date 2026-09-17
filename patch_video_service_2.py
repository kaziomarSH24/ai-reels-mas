import os

with open("python_engine/app/services/video_service.py", "r") as f:
    content = f.read()

# Fix yt-dlp format command
old_yt_dlp = """            dl_cmd = [
                "yt-dlp",
                "--cookies", "/var/www/cookies.txt",
                "-f", "bestvideo[ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]/mp4",
                "--download-sections", f"*{dl_start}-{dl_end}",
                "--force-keyframes-at-cuts",
                "-o", raw_path,
                clip['source_url']
            ]"""

new_yt_dlp = """            dl_cmd = [
                "yt-dlp",
                "--cookies", "/var/www/cookies.txt",
                "-f", "best",
                "--download-sections", f"*{dl_start}-{dl_end}",
                "--force-keyframes-at-cuts",
                "-o", raw_path,
                clip['source_url']
            ]"""

# Fix FFmpeg text position, Bengali text rendering (text_shaping), and audio stream mapping
old_ffmpeg = """            vf_filter = (
                "scale=-1:1920,crop=1080:1920,setsar=1," # Force SAR to 1 to avoid concat issues
                f"drawtext=fontfile='{font_path}':textfile='{target_txt_path}':fontcolor=yellow:fontsize=120:x=(w-text_w)/2:y=200:box=1:boxcolor=black@0.8:boxborderw=30,"
                f"drawtext=fontfile='{font_path}':textfile='{eng_txt_path}':fontcolor=white:fontsize=80:x=(w-text_w)/2:y=(h/2)-200:box=1:boxcolor=black@0.6:boxborderw=20,"
                f"drawtext=fontfile='{font_path}':textfile='{ben_txt_path}':fontcolor=#00FF00:fontsize=70:x=(w-text_w)/2:y=(h/2)+100:box=1:boxcolor=black@0.6:boxborderw=20"
            )
            
            # Ensure output is strictly 1080x1920, 30fps, 44100Hz audio so concat doesn't fail due to mismatch
            ffmpeg_cmd = [
                "ffmpeg", "-y",
                "-i", raw_path,
                "-vf", vf_filter,
                "-r", "30",
                "-c:v", "libx264",
                "-preset", "fast",
                "-c:a", "aac",
                "-ar", "44100",
                proc_path
            ]"""

new_ffmpeg = """            vf_filter = (
                "scale=-1:1920,crop=1080:1920,setsar=1," # Force SAR to 1 to avoid concat issues
                f"drawtext=fontfile='{font_path}':textfile='{target_txt_path}':fontcolor=yellow:fontsize=130:x=(w-text_w)/2:y=250:box=1:boxcolor=black@0.8:boxborderw=30,"
                f"drawtext=fontfile='{font_path}':textfile='{eng_txt_path}':fontcolor=white:fontsize=75:x=(w-text_w)/2:y=h-450:box=1:boxcolor=black@0.6:boxborderw=20,"
                f"drawtext=fontfile='{font_path}':textfile='{ben_txt_path}':text_shaping=1:fontcolor=#00FF00:fontsize=75:x=(w-text_w)/2:y=h-250:box=1:boxcolor=black@0.6:boxborderw=20"
            )
            
            # Ensure output is strictly 1080x1920, 30fps, 44100Hz audio so concat doesn't fail due to mismatch
            # Also fallback to anullsrc if audio is missing
            ffmpeg_cmd = [
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

content = content.replace(old_yt_dlp, new_yt_dlp).replace(old_ffmpeg, new_ffmpeg)

with open("python_engine/app/services/video_service.py", "w") as f:
    f.write(content)
