"""Ghép ảnh bìa main.webp: ảnh hôn (2W4A4516) mờ dần ở trên, chữ "Thanh ♡ Ly" + ngày cưới, ảnh đứng (main.jpg) ở dưới."""
import os
import numpy as np
from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageFilter

IMG = "assets/img"
TOP_PHOTO = "2W4A4516.jpg"
BOTTOM_PHOTO = "main.jpg"
OUT = "main.webp"
W, H = 1600, 2400
SCRIPT_FONT = "C:/Windows/Fonts/ITCEDSCR.TTF"
SERIF_FONT = "C:/Windows/Fonts/GARA.TTF"
TEXT_COLOR = (58, 56, 58)


def smooth(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def load(name, max_side=None):
    im = Image.open(os.path.join(IMG, name))
    return ImageOps.exif_transpose(im).convert("RGB")


def background(src):
    """Nền studio: màu trung bình theo từng hàng ở hai mép ảnh dưới, kéo cho phủ toàn khung."""
    a = np.asarray(src, np.float32)
    edge = np.concatenate([a[:, :40], a[:, -40:]], axis=1).mean(axis=1)  # (h, 3)
    col = np.asarray(Image.fromarray(edge[:, None, :].astype(np.uint8)).resize((1, H), Image.BICUBIC), np.float32)
    return np.repeat(col, W, axis=1)


def paste_faded(canvas, layer, x, y, alpha):
    h, w = alpha.shape
    region = canvas[max(y, 0):y + h, max(x, 0):x + w]
    ly, lx = max(-y, 0), max(-x, 0)
    l = layer[ly:ly + region.shape[0], lx:lx + region.shape[1]]
    a = alpha[ly:ly + region.shape[0], lx:lx + region.shape[1], None]
    region[:] = l * a + region * (1 - a)


def main():
    bottom = load(BOTTOM_PHOTO)
    canvas = background(bottom)

    # Ảnh đứng cả người ở nửa dưới
    s = 0.613
    bw, bh = round(bottom.width * s), round(bottom.height * s)
    b = np.asarray(bottom.resize((bw, bh), Image.LANCZOS), np.float32)
    bx, by = 247, 851
    xs, ys = np.arange(bw), np.arange(bh)
    alpha = smooth(0, 160, ys)[:, None] * (smooth(0, 140, xs) * smooth(0, 140, bw - xs))[None, :]
    paste_faded(canvas, b, bx, by, alpha)

    # Ảnh hôn ở nửa trên, mờ dần xuống dưới và hai bên
    top = load(TOP_PHOTO)
    s = 0.299
    tw, th = round(top.width * s), round(top.height * s)
    t = np.asarray(top.resize((tw, th), Image.LANCZOS), np.float32)
    tx, ty = -8, -143
    xs, ys = np.arange(tw) + tx, np.arange(th) + ty  # toạ độ trên khung
    alpha = (1 - smooth(640, 1080, ys))[:, None] * (smooth(60, 300, xs) * (1 - smooth(W - 300, W - 40, xs)))[None, :]
    paste_faded(canvas, t, tx, ty, alpha)

    page = Image.fromarray(np.clip(canvas, 0, 255).round().astype(np.uint8))

    # Chữ "Thanh ♡ Ly"
    font = ImageFont.truetype(SCRIPT_FONT, 300)
    left, right = "Thanh", "Ly"
    heart_w, gap = 140, 55
    lw = font.getlength(left)
    rw = font.getlength(right)
    total = lw + gap + heart_w + gap + rw
    x0, base = (W - total) / 2, 960
    text = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(text)
    d.text((x0, base), left, font=font, fill=255, anchor="ls")
    d.text((x0 + lw + gap * 2 + heart_w, base), right, font=font, fill=255, anchor="ls")
    # trái tim nét mảnh
    hx, hy = x0 + lw + gap + heart_w / 2, base - 95
    tt = np.linspace(0, 2 * np.pi, 400)
    px = 16 * np.sin(tt) ** 3
    py = -(13 * np.cos(tt) - 5 * np.cos(2 * tt) - 2 * np.cos(3 * tt) - np.cos(4 * tt))
    k = heart_w / 34
    d.line([(hx + u * k, hy + v * k) for u, v in zip(px, py)] + [(hx + px[0] * k, hy + py[0] * k)], fill=255, width=9, joint="curve")

    # Ngày cưới giữa hai đường kẻ
    date_font = ImageFont.truetype(SERIF_FONT, 54)
    date = "1 6  .  1 1  .  2 0 2 6"
    dy = base + 110
    dw = date_font.getlength(date)
    d.text((W / 2, dy), date, font=date_font, fill=235, anchor="mm")
    for sgn in (-1, 1):
        a = W / 2 + sgn * (dw / 2 + 30)
        d.line([(a, dy), (a + sgn * 220, dy)], fill=220, width=3)

    glow = text.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(10))
    page = Image.composite(Image.new("RGB", (W, H), (255, 255, 255)), page, glow.point(lambda v: int(v * 0.6)))
    page = Image.composite(Image.new("RGB", (W, H), TEXT_COLOR), page, text)

    dst = os.path.join(IMG, OUT)
    page.save(dst, "WEBP", quality=92, method=6)
    print(OUT, page.size, os.path.getsize(dst) // 1024, "KB")


if __name__ == "__main__":
    main()
