import random

from io import BytesIO
from PIL import Image, ImageDraw, ImageFont


def create_setu():
    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    ccolor = (
        max(color) + min(color) - color[0],
        max(color) + min(color) - color[1],
        max(color) + min(color) - color[2],
    )

    iml = Image.new("RGB", (300, 300), color)
    imr = Image.new("RGB", (300, 300), ccolor)

    frames = []

    for _ in range(10):
        img = Image.new("RGB", (600, 300))
        img.paste(imr, (300, 0))
        img.paste(iml, (0, 0))
        text = ImageDraw.Draw(img)
        FZDBSJWFont = ImageFont.truetype("./font/FZDBSJW.TTF", random.randint(120, 220))
        text.text(
            (random.randint(10, 100), random.randint(10, 100)),
            "色",
            font=FZDBSJWFont,
            fill=ccolor,
        )
        FZDBSJWFont = ImageFont.truetype("./font/FZDBSJW.TTF", random.randint(120, 220))
        text.text(
            (random.randint(320, 380), random.randint(10, 100)),
            "图",
            font=FZDBSJWFont,
            fill=color,
        )
        frames.append(img)

        img = Image.new("RGB", (600, 300))
        img.paste(iml, (300, 0))
        img.paste(imr, (0, 0))
        text = ImageDraw.Draw(img)
        FZDBSJWFont = ImageFont.truetype("./font/FZDBSJW.TTF", random.randint(120, 220))
        text.text(
            (random.randint(10, 100), random.randint(10, 100)),
            "色",
            font=FZDBSJWFont,
            fill=color,
        )
        FZDBSJWFont = ImageFont.truetype("./font/FZDBSJW.TTF", random.randint(120, 220))
        text.text(
            (random.randint(320, 380), random.randint(10, 100)),
            "图",
            font=FZDBSJWFont,
            fill=ccolor,
        )
        frames.append(img)

    image = BytesIO()
    frames[0].save(
        image,
        format="GIF",
        append_images=frames[1:],
        save_all=True,
        duration=120,
        loop=0,
    )
    return image.getvalue()
