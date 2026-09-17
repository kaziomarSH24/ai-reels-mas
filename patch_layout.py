import re

with open("python_engine/app/services/video_service.py", "r") as f:
    content = f.read()

# Replace the text overlay logic
new_overlay_logic = """
            # Create a 1080x1920 transparent image
            img = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            target = str(clip.get('target_word', '')).strip().upper()
            eng_text = str(clip.get('english_text', '')).strip()
            ben_text = str(clip.get('bengali_text', '')).strip()

            try:
                font_eng = ImageFont.truetype(font_path, 80)
                font_ben = ImageFont.truetype(font_path, 80)
                font_promo_red = ImageFont.truetype(font_path, 70)
                font_promo_blue = ImageFont.truetype(font_path, 65)
            except:
                font_eng = ImageFont.load_default()
                font_ben = ImageFont.load_default()
                font_promo_red = ImageFont.load_default()
                font_promo_blue = ImageFont.load_default()

            def wrap_text(text, font, max_width):
                words = text.split()
                lines = []
                current_line = ""
                for word in words:
                    test_line = current_line + word + " "
                    bbox = draw.textbbox((0, 0), test_line, font=font)
                    w = bbox[2] - bbox[0]
                    if w <= max_width:
                        current_line = test_line
                    else:
                        if current_line:
                            lines.append(current_line.strip())
                        current_line = word + " "
                if current_line:
                    lines.append(current_line.strip())
                return lines

            # 1. Top Text (English in Red, Bengali in Blue)
            # We have 656px of white space at the top. Let's start around y=100
            top_y_start = 120
            
            eng_lines = wrap_text(eng_text, font_eng, 1000)
            for line in eng_lines:
                bbox = draw.textbbox((0, 0), line, font=font_eng)
                w = bbox[2] - bbox[0]
                h = bbox[3] - bbox[1]
                x = (1080 - w) / 2
                draw.text((x, top_y_start), line, font=font_eng, fill=(230, 0, 0, 255))
                top_y_start += h + 20

            top_y_start += 30 # space before bengali
            
            ben_lines = wrap_text(ben_text, font_ben, 1000)
            for line in ben_lines:
                bbox = draw.textbbox((0, 0), line, font=font_ben)
                w = bbox[2] - bbox[0]
                h = bbox[3] - bbox[1]
                x = (1080 - w) / 2
                draw.text((x, top_y_start), line, font=font_ben, fill=(0, 0, 200, 255))
                top_y_start += h + 20

            # 2. Bottom Text (Promo)
            # Video takes center 608px (656 to 1264). Bottom starts at 1264. Let's start at 1350
            bottom_y_start = 1350
            
            promo_lines = [
                ("Advanced English", font_eng, (0, 0, 200, 255)),
                ("sentences এর ২ টি PDF", font_ben, (0, 0, 200, 255)),
                ("কিনতে যোগাযোগ করুন।", font_ben, (0, 0, 200, 255)),
            ]
            
            for text, font, color in promo_lines:
                bbox = draw.textbbox((0, 0), text, font=font)
                w = bbox[2] - bbox[0]
                h = bbox[3] - bbox[1]
                x = (1080 - w) / 2
                draw.text((x, bottom_y_start), text, font=font, fill=color)
                bottom_y_start += h + 15
                
            bottom_y_start += 30
            
            # Bottom Promo Contact (Left and Right aligned roughly, or centered)
            # Left: মাত্র ৯৯ টাকায়, Right: Whats app 017XXXXXXX
            left_text = "মাত্র ৯৯ টাকায়"
            right_text_1 = "Whats app"
            right_text_2 = "01795114695"
            
            bbox_left = draw.textbbox((0, 0), left_text, font=font_promo_red)
            draw.text((80, bottom_y_start + 40), left_text, font=font_promo_red, fill=(230, 0, 0, 255))
            
            bbox_right1 = draw.textbbox((0, 0), right_text_1, font=font_promo_blue)
            draw.text((1000 - (bbox_right1[2]-bbox_right1[0]), bottom_y_start), right_text_1, font=font_promo_blue, fill=(0, 0, 100, 255))
            
            bbox_right2 = draw.textbbox((0, 0), right_text_2, font=font_promo_blue)
            draw.text((1000 - (bbox_right2[2]-bbox_right2[0]), bottom_y_start + 60), right_text_2, font=font_promo_blue, fill=(0, 0, 100, 255))

            img.save(overlay_img_path)
"""

# Extract the region between "img = Image.new" and "img.save(overlay_img_path)"
pattern = re.compile(r"(\s*# Create a 1080x1920 transparent image\s*img = Image\.new.*?)img\.save\(overlay_img_path\)\n", re.DOTALL)
content = pattern.sub(new_overlay_logic, content)

# Now fix the ffmpeg_cmd filter_complex
old_ffmpeg = '''            ffmpeg_cmd = [
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
            ]'''

new_ffmpeg = '''            ffmpeg_cmd = [
                "ffmpeg", "-y",
                "-i", raw_path,
                "-i", overlay_img_path,
                "-filter_complex", "[0:v]scale=1080:-1,setsar=1[scaled_vid];color=c=white:s=1080x1920:r=30[bg];[bg][scaled_vid]overlay=0:(H-h)/2[vid_on_bg];[vid_on_bg][1:v]overlay=0:0[v]",
                "-map", "[v]",
                "-map", "0:a?",
                "-r", "30",
                "-c:v", "libx264",
                "-preset", "fast",
                "-c:a", "aac",
                "-ar", "44100",
                "-ac", "2",
                proc_path
            ]'''

content = content.replace(old_ffmpeg, new_ffmpeg)

with open("python_engine/app/services/video_service.py", "w") as f:
    f.write(content)

