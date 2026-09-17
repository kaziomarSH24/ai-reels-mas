with open("python_engine/app/services/video_service.py", "r") as f:
    content = f.read()

content = content.replace(
    '"{dl_start}-{dl_end}",\n                "--force-keyframes-at-cuts",\n                "-o", raw_path,\n                clip[\'source_url\']',
    '"{dl_start}-{dl_end}",\n                "--force-keyframes-at-cuts",\n                "-o", raw_path,\n                clip[\'source_url\']'
)

# Replace the format string in generate_compilation_reel
old_str = '"-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best",'
new_str = '"-f", "bestvideo[ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]/mp4",'
content = content.replace(old_str, new_str)

with open("python_engine/app/services/video_service.py", "w") as f:
    f.write(content)
