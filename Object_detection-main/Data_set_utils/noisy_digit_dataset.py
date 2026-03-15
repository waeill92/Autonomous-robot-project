from PIL import Image, ImageDraw, ImageFont
import numpy as np
import random

IMG_SIZE = 224  # final image size
DIGIT_SIZE = 100  # size of digit patch

# create random background
bg_color = tuple(np.random.randint(100, 255, 3))  # RGB light colors
bg = Image.new("RGB", (IMG_SIZE, IMG_SIZE), color=bg_color)

# create digit patch with white background
digit_canvas = Image.new("L", (DIGIT_SIZE, DIGIT_SIZE), color=255)
draw = ImageDraw.Draw(digit_canvas)
font = ImageFont.truetype("fonts/RobotoMono-Regular.ttf", size=80)
draw.text((10,10), "3", font=font, fill=0)

# optionally transform digit_canvas (rotation, noise)

# paste digit patch onto background at random position
x = random.randint(0, IMG_SIZE - DIGIT_SIZE)
y = random.randint(0, IMG_SIZE - DIGIT_SIZE)
bg.paste(digit_canvas.convert("RGB"), (x, y))

bg.show()
