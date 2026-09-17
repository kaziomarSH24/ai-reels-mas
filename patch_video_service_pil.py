import re

with open("python_engine/app/services/video_service.py", "r") as f:
    content = f.read()

import_code = """import os
import subprocess
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import textwrap"""

content = re.sub(r'import os\nimport subprocess\nfrom datetime import datetime', import_code, content)

# Replace the text file generation and FFmpeg command in generate_compilation_reel
old_ffmpeg_block = """            wrapped_eng = textwrap.fill(clip['english_text'].strip(), width=25)
            wrapped_ben = textwrap.fill(clip['bengali_text'].strip(), width=25)
            
            eng_txt_path = os.path.join(self.tmp_dir, f"eng_{i}.txt")
            ben_txt_path = os.path.join(self.tmp_dir, f"ben_{i}.txt")
            with open(eng_txt_path, "w", encoding="utf-8") as f:
                f.write(wrapped_eng)
            with open(ben_txt_path, "w", encoding="utf-8") as f:
                f.write(wrapped_ben)
                
            # Add target word at the very top!
            target_word = clip.get('target_word', '').upper()
            target_txt_path = os.path.join(self.tmp_dir, f"target_{i}.txt")
            with open(target_txt_path, "w", encoding="utf-8") as f:
                f.write(target_word)
                
            font_path = "/tmp/HindSiliguri-Bold.ttf"
            vf_filter = (
                "scale=-1:1920,crop=1080:1920,setsar=1," # Force SAR to 1 to avoid concat issues
                f"drawtext=fontfile='{font_path}':textfile='{target_txt_path}':fontcolor=yellow:fontsize=130:x=(w-text_w)/2:y=250:box=1:boxcolor=black@0.8:boxborderw=30,"
                f"drawtext=fontfile='{font_path}':textfile='{eng_txt_path}':fontcolor=white:fontsize=75:x=(w-text_w)/2:y=h-450:box=1:boxcolor=black@0.6:boxborderw=20,"
                f"drawtext=fontfile='{font_path}':textfile='{ben_txt_path}':text_shaping=1:fontcolor=#00FF00:fontsize=75:x=(w-text_w)/2:y=h-250:box=1:boxcolor=black@0.6:boxborderw=20"
            )
            
            ffmpeg_cmd = [
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
            ]
            ff_proc = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            if os.path.exists(proc_path):
                processed_files.append(proc_path)
                
            try:
                os.remove(raw_path)
                os.remove(eng_txt_path)
                os.remove(ben_txt_path)
                os.remove(target_txt_path)
            except:
                pass"""

new_ffmpeg_block = """            target_word = clip.get('target_word', '').upper()
            english_text = clip['english_text'].strip()
            bengali_text = clip['bengali_text'].strip()
            
            font_path = "/tmp/HindSiliguri-Bold.ttf"
            
            # Create transparent PIL image
            img = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            try:
                font_target = ImageFont.truetype(font_path, 130)
                font_eng = ImageFont.truetype(font_path, 75)
                font_ben = ImageFont.truetype(font_path, 75)
            except:
                font_target = ImageFont.load_default()
                font_eng = ImageFont.load_default()
                font_ben = ImageFont.load_default()
            
            # Target Word
            bbox_temp = draw.textbbox((0, 0), target_word, font=font_target)
            w = bbox_temp[2] - bbox_temp[0]
            x = (1080 - w) / 2
            y = 250
            bbox = draw.textbbox((x, y), target_word, font=font_target)
            draw.rectangle((bbox[0] - 30, bbox[1] - 20, bbox[2] + 30, bbox[3] + 20), fill=(0, 0, 0, 204))
            draw.text((x, y), target_word, font=font_target, fill="yellow")

            # English Text
            eng_wrapped = textwrap.fill(english_text, width=22)
            bbox_temp = draw.multiline_textbbox((0, 0), eng_wrapped, font=font_eng, align="center")
            w = bbox_temp[2] - bbox_temp[0]
            h = bbox_temp[3] - bbox_temp[1]
            x = (1080 - w) / 2
            y = 1920 - 450 - h
            bbox = draw.multiline_textbbox((x, y), eng_wrapped, font=font_eng, align="center")
            draw.rectangle((bbox[0] - 20, bbox[1] - 20, bbox[2] + 20, bbox[3] + 20), fill=(0, 0, 0, 153))
            draw.multiline_text((x, y), eng_wrapped, font=font_eng, fill="white", align="center")

            # Bengali Text
            ben_wrapped = textwrap.fill(bengali_text, width=22)
            bbox_temp = draw.multiline_textbbox((0, 0), ben_wrapped, font=font_ben, align="center")
            w = bbox_temp[2] - bbox_temp[0]
            h = bbox_temp[3] - bbox_temp[1]
            x = (1080 - w) / 2
            y = 1920 - 150 - h
            bbox = draw.multiline_textbbox((x, y), ben_wrapped, font=font_ben, align="center")
            draw.rectangle((bbox[0] - 20, bbox[1] - 20, bbox[2] + 20, bbox[3] + 20), fill=(0, 0, 0, 153))
            draw.multiline_text((x, y), ben_wrapped, font=font_ben, fill="#00FF00", align="center")

            overlay_img_path = os.path.join(self.tmp_dir, f"overlay_{i}_{output_filename}.png")
            img.save(overlay_img_path)
            
            ffmpeg_cmd = [
                "ffmpeg", "-y",
                "-i", raw_path,
                "-i", overlay_img_path,
                "-filter_complex", "[0:v]scale=-1:1920,crop=1080:1920,setsar=1[bg];[bg][1:v]overlay=0:0[v]",
                "-map", "[v]",
                "-map", "0:a?",
                "-r", "30",
                "-c:v", "libx264",
                "-preset", "fast",
                "-c:a", "aac",
                "-ar", "44100",
                "-ac", "2",
                proc_path
            ]
            ff_proc = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            if os.path.exists(proc_path):
                processed_files.append(proc_path)
            else:
                print(f"[FFmpeg ERROR] {ff_proc.stderr}")
                
            try:
                os.remove(raw_path)
                os.remove(overlay_img_path)
            except:
                pass"""

content = content.replace(old_ffmpeg_block, new_ffmpeg_block)
with open("python_engine/app/services/video_service.py", "w") as f:
    f.write(content)
