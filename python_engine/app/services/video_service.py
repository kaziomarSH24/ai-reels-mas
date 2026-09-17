import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

class VideoService:
    def __init__(self):
        self.tmp_dir = "/tmp/snapclip/reels"
        self.output_dir = "/var/www/public/generated_reels"
        os.makedirs(self.tmp_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

    def _time_to_seconds(self, time_str):
        h, m, s = time_str.split(':')
        return int(h) * 3600 + int(m) * 60 + float(s)

    def extract_and_crop_clip(self, source_url: str, start_time: str, duration: float, english_text: str, bengali_text: str, output_filename: str) -> str:
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


    
    def _get_gemini_shortened_text(self, target_word: str, english_text: str, bengali_text: str):
        import os, requests, json
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return english_text, bengali_text, ""
            
        prompt = (
            f"You are a helpful dictionary and translator. The user wants a short, punchy video subtitle for the word '{target_word}'. "
            f"The full subtitle is: '{english_text}'. "
            "1. Extract ONLY the exact sentence that contains the target word (remove surrounding unnecessary context). "
            "2. Translate that exact short sentence into natural Bengali. "
            f"3. Provide the exact dictionary meaning in Bengali for the specific word '{target_word}'. "
            "Return ONLY a valid JSON object with keys: 'short_english', 'short_bengali', 'target_word_bengali_meaning'."
        )
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"}
        }
        try:
            res = requests.post(url, json=payload, timeout=10)
            data = res.json()
            text = data['candidates'][0]['content']['parts'][0]['text']
            parsed = json.loads(text)
            return parsed.get('short_english', english_text), parsed.get('short_bengali', bengali_text), parsed.get('target_word_bengali_meaning', '')
        except Exception as e:
            print(f"Gemini error: {e}")
            return english_text, bengali_text, ""

    def generate_compilation_reel(self, clips: list, output_filename: str) -> str:
        import textwrap
        import urllib.parse
        processed_files = []
        
        for i, clip in enumerate(clips):
            print(f"[VideoService] Processing clip {i+1}/{len(clips)}: {clip.get('target_word', '')}")
            start_sec = self._time_to_seconds(clip['start_time'])
            end_sec = start_sec + clip['duration']
            dl_start = max(0, start_sec - 1)
            dl_end = end_sec + 1
            
            raw_path = os.path.join(self.tmp_dir, f"raw_comp_{i}_{output_filename}")
            proc_path = os.path.join(self.tmp_dir, f"proc_comp_{i}_{output_filename}")
            overlay_img_path = os.path.join(self.tmp_dir, f"overlay_{i}_{output_filename}.png")
            
            dl_cmd = [
                "yt-dlp",
                "--cookies", "/var/www/cookies.txt",
                "-f", "bestvideo[ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]/mp4",
                "--download-sections", f"*{dl_start}-{dl_end}",
                "--force-keyframes-at-cuts",
                "-o", raw_path,
                clip['source_url']
            ]
            dl_proc = subprocess.run(dl_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            if not os.path.exists(raw_path):
                continue
                
            # --- GEMINI EXTRACTION ---
            target = str(clip.get('target_word', '')).strip().upper()
            eng_text = str(clip.get('english_text', '')).strip()
            ben_text = str(clip.get('bengali_text', '')).strip()
            
            short_eng, short_ben, word_meaning = self._get_gemini_shortened_text(target, eng_text, ben_text)
            
            # --- PIL TEXT GENERATION ---
            font_path = "/tmp/HindSiliguri-Bold.ttf"
            img = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            try:
                font_word = ImageFont.truetype(font_path, 80)
                font_eng = ImageFont.truetype(font_path, 65)
                font_ben = ImageFont.truetype(font_path, 65)
            except:
                font_word = ImageFont.load_default()
                font_eng = ImageFont.load_default()
                font_ben = ImageFont.load_default()

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
                
            def draw_rounded_text(lines, font, y_start, text_color, bg_color, padding=30):
                current_y = y_start
                for line in lines:
                    bbox = draw.textbbox((0, 0), line, font=font)
                    w = bbox[2] - bbox[0]
                    h = bbox[3] - bbox[1]
                    x = (1080 - w) / 2
                    
                    rect_box = [x - padding, current_y - padding/2, x + w + padding, current_y + h + padding]
                    draw.rounded_rectangle(rect_box, radius=20, fill=bg_color)
                    draw.text((x, current_y), line, font=font, fill=text_color)
                    current_y += h + padding * 2 + 10
                return current_y

            # 1. Top Text: Target Word + Meaning
            target_display = target
            if word_meaning:
                target_display = f"{target} - {word_meaning}"
                
            y = 200
            y = draw_rounded_text([target_display], font_word, y, text_color=(0,0,0,255), bg_color=(255,215,0,255))
            
            # 2. Middle Text: Short English
            y += 20
            eng_lines = wrap_text(short_eng, font_eng, 900)
            y = draw_rounded_text(eng_lines, font_eng, y, text_color=(255,255,255,255), bg_color=(0,0,0,200))
            
            # 3. Bottom Text: Short Bengali
            y = 1350
            ben_lines = wrap_text(short_ben, font_ben, 900)
            y = draw_rounded_text(ben_lines, font_ben, y, text_color=(144,238,144,255), bg_color=(0,0,0,200))

            img.save(overlay_img_path)
            
            # --- FFMPEG: Blurred Background + Centered Video + Overlay ---
            # [0:v] split into two streams: bg_raw and fg_raw
            # bg_raw -> scale to cover 1080x1920, crop center, blur -> bg
            # fg_raw -> scale to width 1080, keep aspect -> fg
            # overlay fg on bg -> vid_on_bg
            # overlay image on vid_on_bg -> final
            filter_complex = (
                "[0:v]split=2[bg_raw][fg_raw];"
                "[bg_raw]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:5[bg];"
                "[fg_raw]scale=1080:-1,setsar=1[fg];"
                "[bg][fg]overlay=0:(H-h)/2[vid_on_bg];"
                "[vid_on_bg][1:v]overlay=0:0[v]"
            )
            
            ffmpeg_cmd = [
                "ffmpeg", "-y",
                "-i", raw_path,
                "-i", overlay_img_path,
                "-filter_complex", filter_complex,
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
                
            try:
                os.remove(raw_path)
                os.remove(overlay_img_path)
            except:
                pass
                
        if not processed_files:
            raise Exception("Failed to process any clips for compilation.")
            
        print("[VideoService] Stitching clips together...")
        final_video_path = os.path.join(self.output_dir, output_filename)
        
        concat_list_path = os.path.join(self.tmp_dir, "concat_list.txt")
        with open(concat_list_path, "w") as f:
            for pf in processed_files:
                f.write(f"file '{pf}'\n")
                
        concat_cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_list_path,
            "-c", "copy",
            final_video_path
        ]
        subprocess.run(concat_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
        for pf in processed_files:
            try:
                os.remove(pf)
            except:
                pass
        try:
            os.remove(concat_list_path)
        except:
            pass
            
        return f"/generated_reels/{output_filename}"


