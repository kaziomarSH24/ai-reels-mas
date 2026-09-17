import re

with open("python_engine/app/services/video_service.py", "r") as f:
    content = f.read()

# We need to replace the draw_rounded_text function inside generate_compilation_reel
old_func = """def draw_rounded_text(lines, font, y_start, text_color, bg_color, padding=30):
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
                return current_y"""

new_func = """def draw_rounded_text(lines, font, y_start, text_color, bg_color, target_words=[], highlight_color=(255,255,0,255), padding=30):
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
                return current_y"""

content = content.replace(old_func, new_func)

# Also update the calls to draw_rounded_text to pass target_words
old_calls = """# 2. Middle Text: Short English
            y += 20
            eng_lines = wrap_text(short_eng, font_eng, 900)
            y = draw_rounded_text(eng_lines, font_eng, y, text_color=(255,255,255,255), bg_color=(0,0,0,200))
            
            # 3. Bottom Text: Short Bengali
            y = 1350
            ben_lines = wrap_text(short_ben, font_ben, 900)
            y = draw_rounded_text(ben_lines, font_ben, y, text_color=(144,238,144,255), bg_color=(0,0,0,200))"""

new_calls = """# Target words for highlighting
            t_words = [target]
            if word_meaning:
                t_words.extend(word_meaning.split(' '))

            # 2. Middle Text: Short English
            y += 20
            eng_lines = wrap_text(short_eng, font_eng, 900)
            y = draw_rounded_text(eng_lines, font_eng, y, text_color=(255,255,255,255), bg_color=(0,0,0,200), target_words=t_words)
            
            # 3. Bottom Text: Short Bengali
            y = 1350
            ben_lines = wrap_text(short_ben, font_ben, 900)
            y = draw_rounded_text(ben_lines, font_ben, y, text_color=(144,238,144,255), bg_color=(0,0,0,200), target_words=t_words)"""

content = content.replace(old_calls, new_calls)

with open("python_engine/app/services/video_service.py", "w") as f:
    f.write(content)
