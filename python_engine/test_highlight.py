from PIL import Image, ImageDraw, ImageFont

img = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)
font = ImageFont.truetype("/tmp/HindSiliguri-Bold.ttf", 65)

def draw_highlighted_text(lines, font, y_start, default_color, bg_color, target_words, highlight_color=(255, 255, 0, 255), padding=30):
    current_y = y_start
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        x_start = (1080 - w) / 2
        
        rect_box = [x_start - padding, current_y - padding/2, x_start + w + padding, current_y + h + padding]
        draw.rounded_rectangle(rect_box, radius=20, fill=bg_color)
        
        words = line.split(' ')
        current_x = x_start
        for word in words:
            is_highlight = False
            for t in target_words:
                if t and t.lower() in word.lower():
                    is_highlight = True
                    break
                    
            color = highlight_color if is_highlight else default_color
            draw.text((current_x, current_y), word, font=font, fill=color)
            
            word_bbox = draw.textbbox((0, 0), word + " ", font=font)
            current_x += (word_bbox[2] - word_bbox[0])
            
        current_y += h + padding * 2 + 10
    return current_y

lines_eng = ["YOU BROUGHT A 90-LB", "ASTHMATIC ONTO MY", "ARMY BASE."]
draw_highlighted_text(lines_eng, font, 400, (255,255,255,255), (0,0,0,200), ["ASTHMATIC"])

lines_ben = ["আপনি আমার সেনা ঘাঁটিতে ৯০", "পাউন্ডের একজন হাঁপানি রোগীকে", "নিয়ে এসেছেন।"]
draw_highlighted_text(lines_ben, font, 1350, (144,238,144,255), (0,0,0,200), ["হাঁপানি", "রোগী"])

img.save("test_highlight.png")
