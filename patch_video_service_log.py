with open("python_engine/app/services/video_service.py", "r") as f:
    content = f.read()

old = """            if not os.path.exists(raw_path):
                print(f"[VideoService] Warning: Failed to download clip {i+1}")
                continue"""

new = """            if not os.path.exists(raw_path):
                print(f"[VideoService] Warning: Failed to download clip {i+1}")
                continue"""

# Wait, I didn't save the proc variable to check stderr
old_dl = """            subprocess.run(dl_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            if not os.path.exists(raw_path):
                print(f"[VideoService] Warning: Failed to download clip {i+1}")"""

new_dl = """            dl_proc = subprocess.run(dl_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            if not os.path.exists(raw_path):
                print(f"[VideoService] Warning: Failed to download clip {i+1}")
                print(f"[yt-dlp ERROR] {dl_proc.stderr}")"""

content = content.replace(old_dl, new_dl)

# also print ffmpeg error
old_ff = """            subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            if os.path.exists(proc_path):"""

new_ff = """            ff_proc = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            if os.path.exists(proc_path):"""

content = content.replace(old_ff, new_ff)

with open("python_engine/app/services/video_service.py", "w") as f:
    f.write(content)
