import os
import subprocess
from PIL import Image, ImageDraw, ImageFont
import whisper
import yt_dlp
import numpy as np

class VideoService:
    """
    VideoService handles the FFmpeg and Whisper AI integration (Phase 2).
    It takes perfectly clean timestamps and texts from Phase 1, crops the video, 
    and overlays the text using Python Imaging Library (PIL).
    ZERO Gemini API calls are made here to ensure high performance and no rate limits.
    """
    def __init__(self):
        """
        Initializes the VideoService, creates temporary directories for processing,
        and pre-loads the Whisper AI base model into memory.
        """
        self.tmp_dir = "/tmp/snapclip"
        self.output_dir = "/var/www/public/generated_reels"
        os.makedirs(self.tmp_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        self.whisper_model = whisper.load_model("base")

    def _find_exact_times_with_whisper(self, audio_path: str, target_word: str):
        """
        Runs Whisper AI on a short audio chunk to find the exact millisecond 
        start and end timestamps of a specific target phrase.
        
        Args:
            audio_path (str): The path to the short audio chunk.
            target_word (str): The exact phrase to search for (whisper_target).
            
        Returns:
            tuple: (start_time, end_time) in seconds, or (None, None) if not found.
        """
        print(f"[Whisper] Searching for exact timestamp of: '{target_word}'")
        try:
            result = self.whisper_model.transcribe(audio_path, word_timestamps=True)
            target_lower = target_word.lower()
            
            for segment in result.get("segments", []):
                words = segment.get("words", [])
                target_parts = target_lower.split()
                
                for i in range(len(words)):
                    match_count = 0
                    start_time = None
                    end_time = None
                    
                    for j, part in enumerate(target_parts):
                        if i + j < len(words):
                            w_text = words[i+j]["word"].lower().strip(".,!?")
                            if part in w_text or w_text in part:
                                if match_count == 0:
                                    start_time = words[i+j]["start"]
                                end_time = words[i+j]["end"]
                                match_count += 1
                                
                    if match_count == len(target_parts):
                        print(f"[Whisper] Found exact match at {start_time}s - {end_time}s")
                        return start_time, end_time
                        
            print(f"[Whisper] Target word '{target_word}' not found in chunk.")
            return None, None
        except Exception as e:
            print(f"[Whisper] Error: {e}")
            return None, None

    def generate_compilation_reel(self, clips: list, output_filename: str) -> str:
        """
        Main pipeline for Phase 2. Takes a list of chosen video clips, crops them,
        applies a blurred background, draws the dynamic text UI (expression, easy example, meaning), 
        and concatenates them all into a final viral reel.
        
        Args:
            clips (list): A list of dictionaries containing video URLs, timestamps, and texts.
            output_filename (str): The name of the final generated .mp4 file.
            
        Returns:
            str: The public URL path to the generated reel.
        """
        print(f"[VideoService] Starting Reel Compilation. Total clips: {len(clips)}")
        processed_files = []

        # Download the Hind Siliguri font if not present for Bengali support
        font_path = "/tmp/HindSiliguri-Bold.ttf"
        if not os.path.exists(font_path):
            subprocess.run(["curl", "-s", "-L", "-o", font_path, "https://github.com/sk-sajib/fonts/raw/master/HindSiliguri/HindSiliguri-Bold.ttf"])

        for idx, clip in enumerate(clips):
            print(f"[VideoService] Processing clip {idx+1}/{len(clips)}...")
            
            source_url = clip.get('source_url')
            # Pad the original timestamps to give Whisper breathing room
            start_sec = max(0, float(clip.get('start_time')) - 5.0) 
            end_sec = float(clip.get('end_time')) + 5.0
            
            expression = str(clip.get('expression', '')).strip()
            whisper_target = str(clip.get('whisper_target', '')).strip()
            if not whisper_target:
                whisper_target = expression
                
            casual_meaning = str(clip.get('casual_meaning', '')).strip()
            easy_example = str(clip.get('easy_example', '')).strip()
            example_translation = str(clip.get('example_translation', '')).strip()

            raw_path = os.path.join(self.tmp_dir, f"raw_{idx}.mp4")
            audio_path = os.path.join(self.tmp_dir, f"audio_{idx}.wav")
            exact_vid_path = os.path.join(self.tmp_dir, f"exact_{idx}.mp4")
            overlay_img_path = os.path.join(self.tmp_dir, f"overlay_{idx}.png")
            proc_path = os.path.join(self.tmp_dir, f"proc_{idx}.mp4")
            
            # Step 1: Download rough chunk using yt-dlp
            ydl_opts = {
                'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': raw_path,
                'download_ranges': yt_dlp.utils.download_range_func(None, [(start_sec, end_sec)]),
                'force_keyframes_at_cuts': True,
                'cookiefile': '/var/www/cookies.txt',
                'quiet': True,
                'no_warnings': True
            }
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([source_url])
            except Exception as e:
                print(f"[VideoService] Download failed for clip {idx}: {e}")
                continue
                
            if not os.path.exists(raw_path):
                continue
                
            # Step 2: Extract Audio to process with Whisper
            subprocess.run([
                "ffmpeg", "-y", "-i", raw_path, "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", audio_path
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Step 3: Whisper Exact Alignment
            exact_start, exact_end = self._find_exact_times_with_whisper(audio_path, whisper_target)
            
            # Use generous padding around the original clip boundaries instead of aggressive Whisper cropping
            # This ensures the full context/sentence is heard.
            requested_start = float(clip.get('start_time'))
            requested_end = float(clip.get('end_time'))
            
            # We rely on the database's start_time and end_time (which represent the full sentence).
            # We add just a tiny 0.5s buffer before and 0.8s buffer after so we don't bleed into other sentences.
            crop_start = 4.5  # 5.0 - 0.5 = 4.5 seconds into the chunk
            crop_dur = (requested_end - requested_start) + 1.3
                
            # Step 4: Micro-crop the video with libx264 re-encoding to fix keyframe blanking
            subprocess.run([
                "ffmpeg", "-y", "-ss", str(crop_start), "-t", str(crop_dur),
                "-i", raw_path, 
                "-c:v", "libx264", "-preset", "ultrafast", 
                "-c:a", "aac",
                exact_vid_path
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Step 5: PIL Overlay Generation for Expression, Meaning, and Example
            img = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            try:
                font_word = ImageFont.truetype(font_path, 90)
                font_meaning = ImageFont.truetype(font_path, 60)
                font_example = ImageFont.truetype(font_path, 50)
            except:
                font_word = ImageFont.load_default()
                font_meaning = ImageFont.load_default()
                font_example = ImageFont.load_default()

            def wrap_text(text, font, max_width):
                """Helper function to wrap long sentences into multiple lines."""
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
                """Helper function to draw text with a beautiful rounded background box."""
                current_y = y_start
                for line in lines:
                    bbox = draw.textbbox((0, 0), line, font=font)
                    w = bbox[2] - bbox[0]
                    h = bbox[3] - bbox[1]
                    x_start = (1080 - w) / 2
                    
                    rect_box = [x_start - padding, current_y - padding/2, x_start + w + padding, current_y + h + padding]
                    draw.rounded_rectangle(rect_box, radius=20, fill=bg_color)
                    
                    draw.text((x_start, current_y), line, font=font, fill=text_color)
                    current_y += h + padding * 2 + 10
                return current_y

            # UI Rendering: Draw Expression (Top)
            y = 300
            y = draw_rounded_text([expression.upper()], font_word, y, text_color=(0,0,0,255), bg_color=(255,215,0,255))
            
            # UI Rendering: Draw Easy Example and Translation (Middle)
            if easy_example:
                y = 1450
                example_lines = wrap_text(easy_example, font_example, 900)
                if example_translation:
                    example_lines.extend(wrap_text(example_translation, font_example, 900))
                draw_rounded_text(example_lines, font_example, y, text_color=(255,255,255,255), bg_color=(0,0,255,200))

            # UI Rendering: Draw Casual Meaning (Bottom)
            if casual_meaning:
                y = 450
                meaning_lines = wrap_text(f"অর্থ: {casual_meaning}", font_meaning, 900)
                draw_rounded_text(meaning_lines, font_meaning, y, text_color=(255,255,255,255), bg_color=(0,150,0,200))

            img.save(overlay_img_path)
            
            # Step 6: FFmpeg composite to burn the PIL image onto the blurred background video
            filter_complex = (
                "[0:v]split=2[bg_raw][fg_raw];"
                "[bg_raw]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:5[bg];"
                "[fg_raw]scale=1080:-1,setsar=1[fg];"
                "[bg][fg]overlay=0:(H-h)/2[vid_on_bg];"
                "[vid_on_bg][1:v]overlay=0:0[v]"
            )
            
            subprocess.run([
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
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            if os.path.exists(proc_path):
                processed_files.append(proc_path)
                
            # Cleanup temporary chunk files
            for f in [raw_path, audio_path, exact_vid_path, overlay_img_path]:
                try: os.remove(f)
                except: pass
                
        if not processed_files:
            raise Exception("Failed to process any clips for compilation.")
            
        print("[VideoService] Stitching all processed clips together...")
        final_video_path = os.path.join(self.output_dir, output_filename)
        
        concat_list_path = os.path.join(self.tmp_dir, "concat_list.txt")
        with open(concat_list_path, "w") as f:
            for pf in processed_files:
                f.write(f"file '{pf}'\n")
                
        # Final Step: Concatenate all micro-crops into one single viral reel
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", concat_list_path, "-c", "copy", final_video_path
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
        # Cleanup processed chunks
        for pf in processed_files:
            try: os.remove(pf)
            except: pass
        try: os.remove(concat_list_path)
        except: pass
            
        return f"/generated_reels/{output_filename}"
