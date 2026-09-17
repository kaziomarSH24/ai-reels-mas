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
bbox = draw.textbbox((0, 0), target_word, font=font_target)
w = bbox[2] - bbox[0]
h = bbox[3] - bbox[1]
x = (1080 - w) / 2
y = 250
# Draw background box
draw.rectangle((x - 30, y - 10, x + w + 30, y + h + 10), fill=(0, 0, 0, 204))
draw.text((x, y), target_word, font=font_target, fill="yellow")

# English Text (wrapped)
eng_wrapped = textwrap.fill(english_text, width=25)
bbox = draw.multiline_textbbox((0, 0), eng_wrapped, font=font_eng, align="center")
w = bbox[2] - bbox[0]
h = bbox[3] - bbox[1]
x = (1080 - w) / 2
y = 1920 - 450 - h # Adjust Y based on height
draw.rectangle((x - 20, y - 10, x + w + 20, y + h + 10), fill=(0, 0, 0, 153))
draw.multiline_text((x, y), eng_wrapped, font=font_eng, fill="white", align="center")

# Bengali Text (wrapped)
ben_wrapped = textwrap.fill(bengali_text, width=25)
bbox = draw.multiline_textbbox((0, 0), ben_wrapped, font=font_ben, align="center")
w = bbox[2] - bbox[0]
h = bbox[3] - bbox[1]
x = (1080 - w) / 2
y = 1920 - 200 - h
draw.rectangle((x - 20, y - 10, x + w + 20, y + h + 10), fill=(0, 0, 0, 153))
draw.multiline_text((x, y), ben_wrapped, font=font_ben, fill="#00FF00", align="center")

img.save("/var/www/test_overlay.png")
