"""Tạo ảnh slide desktop (khung ngang 16:9) từ ảnh gốc.
- Ảnh ngang: thu về rộng 2200px.
- Ảnh dọc: đặt nguyên vẹn ở giữa, hai bên là chính ảnh đó phóng to + làm mờ,
  nên không bị cắt người và không phải phóng to ảnh chính (không vỡ ảnh).
"""
import os
from PIL import Image, ImageFilter, ImageEnhance

SRC_DIR = "assets/img"
SLIDES = ["pic", "pic1", "pic3", "bg2", "bia", "lg4"]  # -> slide1..slide6.webp
W, H = 2560, 1440


def landscape_from_portrait(img, W=W, H=H):
    # Nền: phủ kín khung, làm mờ và tối nhẹ
    scale = max(W / img.width, H / img.height)
    bg = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    left, top = (bg.width - W) // 2, (bg.height - H) // 2
    bg = bg.crop((left, top, left + W, top + H)).filter(ImageFilter.GaussianBlur(40))
    bg = ImageEnhance.Brightness(bg).enhance(0.8)

    # Bóng mờ quanh ảnh chính
    fg = img.resize((round(img.width * H / img.height), H), Image.LANCZOS)
    x = (W - fg.width) // 2
    shadow = Image.new("L", (W, H), 0)
    shadow.paste(255, (x, 0, x + fg.width, H))
    shadow = shadow.filter(ImageFilter.GaussianBlur(30))
    bg = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), bg, shadow.point(lambda v: v * 0.45))

    bg.paste(fg, (x, 0))
    return bg


def main():
    for i, name in enumerate(SLIDES, 1):
        img = Image.open(os.path.join(SRC_DIR, name + ".jpg")).convert("RGB")
        if img.height > img.width:
            out = landscape_from_portrait(img)
        else:
            out = img.resize((2200, round(img.height * 2200 / img.width)), Image.LANCZOS) if img.width > 2200 else img
        dst = os.path.join(SRC_DIR, f"slide{i}.webp")
        out.save(dst, "WEBP", quality=78, method=6)
        print(f"{dst} <- {name}.jpg {out.size} {os.path.getsize(dst) // 1024} KB")


if __name__ == "__main__":
    main()
