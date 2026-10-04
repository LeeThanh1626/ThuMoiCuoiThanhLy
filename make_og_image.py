"""Ảnh xem trước khi gửi link (Zalo/Facebook/Messenger): JPG 1200x630, ảnh bìa ở giữa trên nền mờ."""
import os
from PIL import Image, ImageFilter, ImageEnhance

SRC = "assets/img/main.webp"
OUT = "assets/img/og-cover.jpg"
W, H = 1200, 630


def main():
    cover = Image.open(SRC).convert("RGB")

    # Nền: ảnh bìa phóng to phủ khung, làm mờ và tối nhẹ
    s = max(W / cover.width, H / cover.height)
    bg = cover.resize((round(cover.width * s), round(cover.height * s)), Image.LANCZOS)
    top = round((bg.height - H) * 0.3)
    bg = bg.crop(((bg.width - W) // 2, top, (bg.width - W) // 2 + W, top + H))
    bg = ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(28))).enhance(0.9)

    # Ảnh bìa nguyên vẹn ở giữa, cao bằng khung
    fg = cover.resize((round(cover.width * H / cover.height), H), Image.LANCZOS)
    bg.paste(fg, ((W - fg.width) // 2, 0))

    bg.save(OUT, "JPEG", quality=88, optimize=True, progressive=True)
    print(OUT, bg.size, os.path.getsize(OUT) // 1024, "KB")


if __name__ == "__main__":
    main()
