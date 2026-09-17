from PIL import Image, ImageDraw, ImageFont

img = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)
font = ImageFont.truetype("/var/www/python_engine/assets/fonts/HindSiliguri-Bold.ttf", 80)
draw.text((100, 100), "পুনর্গঠনে ফিরে আসা", font=font, fill="white")
img.save("test_bengali.png")
