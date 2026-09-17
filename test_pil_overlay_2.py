from PIL import Image, ImageDraw, ImageFont
import textwrap

img = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)
font_target = ImageFont.truetype("/tmp/HindSiliguri-Bold.ttf", 130)
font_eng = ImageFont.truetype("/tmp/HindSiliguri-Bold.ttf", 75)
font_ben = ImageFont.truetype("/tmp/HindSiliguri-Bold.ttf", 75)

target_word = "KIDDING"
english_text = "you gotta be kidding me you start there where the road begins"
bengali_text = "তুমি কি আমার সাথে মজা করছ? যেখানে রাস্তা শুরু"

# Target Word
bbox_temp = draw.textbbox((0, 0), target_word, font=font_target)
w = bbox_temp[2] - bbox_temp[0]
x = (1080 - w) / 2
y = 250
bbox = draw.textbbox((x, y), target_word, font=font_target)
draw.rectangle((bbox[0] - 30, bbox[1] - 20, bbox[2] + 30, bbox[3] + 20), fill=(0, 0, 0, 204))
draw.text((x, y), target_word, font=font_target, fill="yellow")

# English Text (wrapped)
eng_wrapped = textwrap.fill(english_text, width=22)
bbox_temp = draw.multiline_textbbox((0, 0), eng_wrapped, font=font_eng, align="center")
w = bbox_temp[2] - bbox_temp[0]
h = bbox_temp[3] - bbox_temp[1]
x = (1080 - w) / 2
y = 1920 - 450 - h
bbox = draw.multiline_textbbox((x, y), eng_wrapped, font=font_eng, align="center")
draw.rectangle((bbox[0] - 20, bbox[1] - 20, bbox[2] + 20, bbox[3] + 20), fill=(0, 0, 0, 153))
draw.multiline_text((x, y), eng_wrapped, font=font_eng, fill="white", align="center")

# Bengali Text (wrapped)
ben_wrapped = textwrap.fill(bengali_text, width=22)
bbox_temp = draw.multiline_textbbox((0, 0), ben_wrapped, font=font_ben, align="center")
w = bbox_temp[2] - bbox_temp[0]
h = bbox_temp[3] - bbox_temp[1]
x = (1080 - w) / 2
y = 1920 - 150 - h
bbox = draw.multiline_textbbox((x, y), ben_wrapped, font=font_ben, align="center")
draw.rectangle((bbox[0] - 20, bbox[1] - 20, bbox[2] + 20, bbox[3] + 20), fill=(0, 0, 0, 153))
draw.multiline_text((x, y), ben_wrapped, font=font_ben, fill="#00FF00", align="center")

img.save("/var/www/test_overlay_2.png")
