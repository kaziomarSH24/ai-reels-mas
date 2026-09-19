import os
import subprocess
import string
import json
from PIL import Image, ImageDraw, ImageFont

class VideoService:
    def __init__(self):
        self.tmp_dir = "/tmp/snapclip/reels"
        self.output_dir = "/var/www/public/generated_reels"
        os.makedirs(self.tmp_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        self._whisper_model = None
        
    def _get_whisper(self):
        if self._whisper_model is None:
            from transformers import pipeline
            print("[VideoService] Loading Whisper AI Model (Transformers Tiny)...")
            self._whisper_model = pipeline(
                "automatic-speech-recognition", 
                model="openai/whisper-tiny",
                chunk_length_s=30,
                return_timestamps="word"
            )
        return self._whisper_model

    def _time_to_seconds(self, time_str):
        time_str = str(time_str).strip()
        if ':' in time_str:
            parts = time_str.split(':')
            if len(parts) == 3:
                h, m, s = parts
                return int(h) * 3600 + int(m) * 60 + float(s)
            elif len(parts) == 2:
                m, s = parts
                return int(m) * 60 + float(s)
        try:
            return float(time_str)
        except:
            return 0.0

    def extract_and_crop_clip(self, source_url: str, start_time: str, duration: float, english_text: str, bengali_text: str, output_filename: str) -> str:
        pass

    def _get_gemini_shortened_text(self, target: str, eng: str, ben: str):
        import os, requests
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key: return "", "", ""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={api_key}"
        prompt = f"""You are an English-to-Bengali vocabulary dictionary.
I have the phrase: "{target}"
Context dialogue: "{eng}"
Bengali dialogue: "{ben}"

Return ONLY the true, contextual dictionary meaning of "{target}" in Bengali.
WARNING: If it is an idiom (like 'piece of cake'), return the FIGURATIVE meaning (e.g. 'খুব সহজ'). DO NOT translate it literally (e.g. do not say 'এক টুকরো কেক').
Keep it extremely short (max 2-3 words). 
Return nothing else."""
        try:
            r = requests.post(url, json={"contents": [{"parts":[{"text": prompt}]}]})
            if r.status_code == 200:
                t = r.json()['candidates'][0]['content']['parts'][0]['text'].strip()
                return "", "", t
        except: pass
        return "", "", ""

    def _find_exact_times_with_whisper(self, audio_path, target_phrase):
        print(f"[WhisperAI] Scanning audio to find exact timestamps for: '{target_phrase}'")
        try:
            model = self._get_whisper()
            result = model(audio_path)
            
            target_clean = target_phrase.translate(str.maketrans('', '', string.punctuation)).lower().split()
            if not target_clean or "chunks" not in result:
                return None, None
                
            chunks = result["chunks"]
            words = []
            for chunk in chunks:
                if 'timestamp' in chunk and chunk['timestamp'][0] is not None and chunk['timestamp'][1] is not None:
                    word_text = chunk['text'].translate(str.maketrans('', '', string.punctuation)).lower().strip()
                    if word_text:
                        words.append((word_text, chunk['timestamp'][0], chunk['timestamp'][1]))
                        
            for i in range(len(words) - len(target_clean) + 1):
                match = True
                for j, t_word in enumerate(target_clean):
                    if t_word not in words[i+j][0] and words[i+j][0] not in t_word:
                        match = False
                        break
                if match:
                    exact_start = words[i][1]
                    exact_end = words[i + len(target_clean) - 1][2]
                    print(f"[WhisperAI] SUCCESS! Found phrase at {exact_start}s to {exact_end}s")
                    return exact_start, exact_end
        except Exception as e:
            print(f"[WhisperAI] Error: {e}")
            
        print(f"[WhisperAI] Failed to find exact phrase in audio.")
        return None, None

    def generate_compilation_reel(self, clips: list[dict], output_filename: str) -> str:
        print(f"[VideoService] Generating Compilation Reel with {len(clips)} clips using Whisper AI...")
        processed_files = []
        gemini_cache = {}
        
        for i, clip in enumerate(clips):
            print(f"Processing Clip {i+1}...")
            start_sec = self._time_to_seconds(clip['start_time'])
            
            dl_start = max(0, start_sec - 5)
            dl_dur = 15 
            
            raw_path = os.path.join(self.tmp_dir, f"raw_padded_{i}.mp4")
            audio_path = os.path.join(self.tmp_dir, f"audio_{i}.wav")
            exact_vid_path = os.path.join(self.tmp_dir, f"exact_{i}.mp4")
            overlay_img_path = os.path.join(self.tmp_dir, f"overlay_{i}.png")
            proc_path = os.path.join(self.tmp_dir, f"proc_{i}.mp4")
            
            dl_cmd = [
                "yt-dlp", "-f", "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                "--download-sections", f"*{dl_start}-{dl_start+dl_dur}",
                "--force-keyframes-at-cuts",
                "--cookies", "/var/www/cookies.txt", 
                "-o", raw_path,
                clip['source_url']
            ]
            subprocess.run(dl_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            if not os.path.exists(raw_path):
                print(f"Failed to download clip {i+1} using yt-dlp section download.")
                continue
                
            subprocess.run(["ffmpeg", "-y", "-i", raw_path, "-vn", "-c:a", "pcm_s16le", audio_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            target_full = str(clip.get('target_word', '')).strip()
            target = target_full.split(' (')[0].strip() if ' (অর্থ:' in target_full else target_full
            
            exact_start, exact_end = self._find_exact_times_with_whisper(audio_path, target)
            
            if exact_start is not None and exact_end is not None:
                crop_start = max(0, exact_start - 0.5) 
                crop_dur = (exact_end - exact_start) + 1.0 
            else:
                print("[VideoService] Whisper failed to find word, falling back to rough timestamp.")
                crop_start = 4.0 
                crop_dur = 4.0
                
            # FIX: We MUST re-encode here instead of using '-c copy'. 
            # yt-dlp downloads sections that often lack keyframes in the middle. 
            # Using '-c copy' to cut exactly at 4.0s results in a broken/blank mp4!
            subprocess.run([
                "ffmpeg", "-y", "-ss", str(crop_start), "-t", str(crop_dur),
                "-i", raw_path, 
                "-c:v", "libx264", "-preset", "ultrafast", 
                "-c:a", "aac",
                exact_vid_path
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
            eng_text = str(clip.get('english_text', '')).strip()
            ben_text = str(clip.get('bengali_text', '')).strip()
            
            dict_meaning = str(clip.get('dictionary_meaning', '')).strip()
            
            if not dict_meaning and ' (অর্থ:' in target_full:
                dict_meaning = target_full.split(' (')[1].strip()
                if dict_meaning.endswith(')'): dict_meaning = dict_meaning[:-1]
                
            if dict_meaning:
                if not dict_meaning.startswith('অর্থ:'):
                    dict_meaning = f"অর্থ: {dict_meaning}"
                short_eng = ""
                short_ben = ""
                word_meaning = dict_meaning
            else:
                if target in gemini_cache:
                    short_eng, short_ben, word_meaning = gemini_cache[target]
                else:
                    short_eng, short_ben, word_meaning = self._get_gemini_shortened_text(target, eng_text, ben_text)
                    word_meaning = f"অর্থ: {word_meaning}"
                    gemini_cache[target] = (short_eng, short_ben, word_meaning)
            
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
                
            def draw_rounded_text(lines, font, y_start, text_color, bg_color, target_words=[], highlight_color=(255,255,0,255), padding=30):
                current_y = y_start
                for line in lines:
                    bbox = draw.textbbox((0, 0), line, font=font)
                    w = bbox[2] - bbox[0]
                    h = bbox[3] - bbox[1]
                    x_start = (1080 - w) / 2
                    
                    rect_box = [x_start - padding, current_y - padding/2, x_start + w + padding, current_y + h + padding]
                    draw.rounded_rectangle(rect_box, radius=20, fill=bg_color)
                    
                    if not target_words:
                        draw.text((x_start, current_y), line, font=font, fill=text_color)
                    else:
                        words = line.split(' ')
                        current_x = x_start
                        for word in words:
                            is_highlight = False
                            for t in target_words:
                                if t and t.lower() in word.lower():
                                    is_highlight = True
                                    break
                            
                            color = highlight_color if is_highlight else text_color
                            draw.text((current_x, current_y), word, font=font, fill=color)
                            
                            word_bbox = draw.textbbox((0, 0), word + " ", font=font)
                            current_x += (word_bbox[2] - word_bbox[0])
                            
                    current_y += h + padding * 2 + 10
                return current_y

            y = 300
            target_display = target.upper()
            y = draw_rounded_text([target_display], font_word, y, text_color=(0,0,0,255), bg_color=(255,215,0,255))
            
            if word_meaning:
                y = 1300
                lines_ben = wrap_text(word_meaning, font_ben, 900)
                draw_rounded_text(lines_ben, font_ben, y, text_color=(255,255,255,255), bg_color=(0,150,0,200))

            img.save(overlay_img_path)
            
            filter_complex = (
                "[0:v]split=2[bg_raw][fg_raw];"
                "[bg_raw]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:5[bg];"
                "[fg_raw]scale=1080:-1,setsar=1[fg];"
                "[bg][fg]overlay=0:(H-h)/2[vid_on_bg];"
                "[vid_on_bg][1:v]overlay=0:0[v]"
            )
            
            ffmpeg_cmd = [
                "ffmpeg", "-y",
                "-i", exact_vid_path,
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
            subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            if os.path.exists(proc_path):
                processed_files.append(proc_path)
                
            for f in [raw_path, audio_path, exact_vid_path, overlay_img_path]:
                try: os.remove(f)
                except: pass
                
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
        subprocess.run(concat_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
        for pf in processed_files:
            try: os.remove(pf)
            except: pass
        try: os.remove(concat_list_path)
        except: pass
            
        return f"/generated_reels/{output_filename}"

