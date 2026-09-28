import re
import sys

sub_path = '/Users/kaziomar/University/SEMESTER 07/AI/Lab-project/python_engine/app/services/subtitle_service.py'
with open(sub_path, 'r') as f:
    content = f.read()

# Replace the command array in subtitle_service.py
old_cmd = 'cmd = [\n                    "yt-dlp",\n                    "--write-auto-subs",'
new_cmd = 'cmd = [\n                    "yt-dlp",\n                    "--js-runtimes", "deno",\n                    "--remote-components", "ejs:github",\n                    "--write-auto-subs",'
content = content.replace(old_cmd, new_cmd)

# Replace the stream_cmd array in subtitle_service.py
old_stream = 'stream_cmd = ["yt-dlp", "-g", video_url]'
new_stream = 'stream_cmd = ["yt-dlp", "--js-runtimes", "deno", "--remote-components", "ejs:github", "-g", video_url]'
content = content.replace(old_stream, new_stream)

with open(sub_path, 'w') as f:
    f.write(content)

video_path = '/Users/kaziomar/University/SEMESTER 07/AI/Lab-project/python_engine/app/services/video_service.py'
with open(video_path, 'r') as f:
    content = f.read()

# Add extractor_args and js_runtimes to ydl_opts
if "'js_runtimes': ['deno']" not in content:
    old_opts = "'cookiefile': '/var/www/storage/app/private/cookies.txt',"
    new_opts = "'cookiefile': '/var/www/storage/app/private/cookies.txt',\n                'js_runtimes': ['deno'],\n                'remote_components': 'ejs:github',"
    content = content.replace(old_opts, new_opts)

with open(video_path, 'w') as f:
    f.write(content)
