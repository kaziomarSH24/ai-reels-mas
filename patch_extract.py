with open("python_engine/app/services/video_service.py", "r") as f:
    content = f.read()

import re

# We need to replace the extract_and_crop_clip body
pattern = re.compile(r"def extract_and_crop_clip.*?pass", re.DOTALL)

new_extract = """def extract_and_crop_clip(self, source_url: str, start_time: str, duration: float, english_text: str, bengali_text: str, output_filename: str) -> str:
        import textwrap
        print(f"[VideoService] Processing and Cropping to 9:16 vertical with Subtitles...")
        
        start_sec = self._time_to_seconds(start_time)
        dl_start = max(0, start_sec - 1)
        dl_end = start_sec + duration + 1
        
        raw_video_path = os.path.join(self.tmp_dir, f"raw_{output_filename}")
        final_video_path = os.path.join(self.output_dir, output_filename)
        overlay_img_path = os.path.join(self.tmp_dir, f"overlay_{output_filename}.png")
        
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
            raise Exception("Failed to download video section.")

        # PIL Text Generation (Letterbox Layout)
        font_path = "/tmp/HindSiliguri-Bold.ttf"
        img = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        eng_text = str(english_text).strip()
        ben_text = str(bengali_text).strip()

        try:
            font_eng = ImageFont.truetype(font_path, 60)
            font_ben = ImageFont.truetype(font_path, 60)
            font_promo_red = ImageFont.truetype(font_path, 55)
            font_promo_blue = ImageFont.truetype(font_path, 55)
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

        # 1. Top Text
        top_y_start = 120
        eng_lines = wrap_text(eng_text, font_eng, 960)
        for line in eng_lines:
            bbox = draw.textbbox((0, 0), line, font=font_eng)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            x = (1080 - w) / 2
            draw.text((x, top_y_start), line, font=font_eng, fill=(230, 0, 0, 255))
            top_y_start += h + 20

        top_y_start += 30
        ben_lines = wrap_text(ben_text, font_ben, 960)
        for line in ben_lines:
            bbox = draw.textbbox((0, 0), line, font=font_ben)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            x = (1080 - w) / 2
            draw.text((x, top_y_start), line, font=font_ben, fill=(0, 0, 200, 255))
            top_y_start += h + 20

        # 2. Bottom Text
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

        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-i", raw_video_path,
            "-i", overlay_img_path,
            "-filter_complex", "[0:v]scale=1080:-1,setsar=1[scaled_vid];color=c=white:s=1080x1920:r=30[bg];[bg][scaled_vid]overlay=0:(H-h)/2[vid_on_bg];[vid_on_bg][1:v]overlay=0:0[v]",
            "-map", "[v]",
            "-map", "0:a?",
            "-c:v", "libx264",
            "-preset", "fast",
            "-c:a", "aac",
            final_video_path
        ]

        ffmpeg_process = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if not os.path.exists(final_video_path):
            raise Exception("FFmpeg failed to process the video.")

        try:
            os.remove(raw_video_path)
            os.remove(overlay_img_path)
        except:
            pass

        return f"/generated_reels/{output_filename}"
"""

content = pattern.sub(new_extract, content)

with open("python_engine/app/services/video_service.py", "w") as f:
    f.write(content)
