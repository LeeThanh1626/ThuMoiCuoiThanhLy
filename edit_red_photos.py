"""Chỉnh ảnh nền rèm đỏ (studio) cho album.

- Nền (tường be, sàn gỗ) -> trắng; rèm, hoa, thảm đỏ giữ nguyên
- Váy / áo vest trắng: sáng hơn theo tỉ lệ (giữ nếp vải), bỏ ám vàng
- KHÔNG nâng sáng toàn ảnh, KHÔNG đụng vào mặt và da: mọi điểm ảnh ngoài nền + vải giữ nguyên gốc

Chạy:  python edit_red_photos.py            (tất cả ảnh)
       python edit_red_photos.py 2W4A4725   (một ảnh)

Toạ độ trong PHOTOS tính theo ảnh thu nhỏ rộng 862px.
"""
import os
import sys
import numpy as np
from PIL import Image, ImageOps, ImageCms, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(ROOT, "assets", "img")
OUT_W = 934
BG_L = 90  # độ sáng nền (Lab 0-100): 95 = trắng tinh, 90 = trắng ngà dịu

PHOTOS = {
    "2W4A4766": {
        "out": "album-04.webp",
        "crop_top": 24,  # px ở ảnh đầu ra
        "person": [(205, 325, 585, 1062), (340, 760, 752, 1062)],
        "faces": [(285, 330, 390, 470), (425, 370, 520, 500)],
        "wall": [(0, 0, 160, 620), (706, 0, 862, 620)],
        "floor": [(0, 940, 175, 1292), (680, 950, 862, 1292)],
    },
    "2W4A4725": {
        "out": "2W4A4725.webp",
        "crop_top": 85,  # bỏ dải trần nhà tối
        "person": [(205, 375, 420, 1040), (370, 420, 605, 1068), (380, 850, 770, 1068)],
        "faces": [(275, 375, 365, 485), (440, 420, 525, 535)],
        "wall": [(0, 0, 200, 1000), (680, 0, 862, 1000)],
        "floor": [(0, 940, 170, 1292), (690, 975, 862, 1292)],
    },
    "2W4A4802": {
        "out": "2W4A4802.webp",
        "crop_top": 108,  # bỏ dải trần nhà tối
        "person": [(225, 400, 405, 1065), (295, 445, 700, 1105)],
        "faces": [(295, 405, 385, 515), (380, 450, 460, 565)],
        "wall": [(0, 0, 205, 1000), (690, 0, 862, 1000)],
        "floor": [(0, 975, 185, 1292), (670, 990, 862, 1292)],
    },
}

srgb = ImageCms.createProfile("sRGB")
lab = ImageCms.createProfile("LAB")
to_lab = ImageCms.buildTransformFromOpenProfiles(srgb, lab, "RGB", "LAB")
to_rgb = ImageCms.buildTransformFromOpenProfiles(lab, srgb, "LAB", "RGB")


def tolab(im):
    x = np.asarray(ImageCms.applyTransform(im, to_lab))
    return np.dstack([x[..., 0].astype(float) / 255 * 100,
                      x[..., 1:].copy().view(np.int8).astype(float)])


def fromlab(x):
    L = np.clip(x[..., 0] / 100 * 255, 0, 255).round().astype(np.uint8)
    ab = np.clip(x[..., 1:], -128, 127).round().astype(np.int8).view(np.uint8)
    return ImageCms.applyTransform(Image.fromarray(np.dstack([L, ab]), "LAB"), to_rgb)


def smooth(m, r):
    img = Image.fromarray((np.clip(m, 0, 1) * 255).astype("uint8"))
    return np.asarray(img.filter(ImageFilter.GaussianBlur(r))).astype(float) / 255


def ramp(v, lo, hi):
    return np.clip((v - lo) / (hi - lo), 0, 1)


def process(name, cfg):
    src = ImageOps.exif_transpose(Image.open(os.path.join(IMG_DIR, name + ".jpg"))).convert("RGB")
    src = src.resize((OUT_W, round(src.height * OUT_W / src.width)), Image.LANCZOS)
    x = tolab(src)
    L, A, B = x[..., 0], x[..., 1], x[..., 2]
    h, w = L.shape
    chroma = np.hypot(A, B)
    yy, xx = np.mgrid[0:h, 0:w]
    s = w / 862

    def boxes(rects):
        m = np.zeros((h, w))
        for x0, y0, x1, y1 in rects:
            m = np.maximum(m, ((xx >= x0 * s) & (xx < x1 * s) & (yy >= y0 * s) & (yy < y1 * s)).astype(float))
        return m

    person = smooth(boxes(cfg["person"]), 6)
    faces = smooth(boxes(cfg["faces"]), 4)
    wall, floor = boxes(cfg["wall"]), boxes(cfg["floor"])

    # 1) Nền -> trắng: trong vùng tường/sàn, chừa màu đỏ và bóng tối trong lùm hoa
    not_red = (1 - ramp(A, 18, 28)) * (1 - ramp(chroma, 22, 32))
    bg = wall * ramp(L, 24, 34) + floor * ramp(L, 8, 16)
    protect = person * np.maximum(1 - floor, ramp(L, 62, 72))
    bg = smooth(np.clip(bg, 0, 1) * not_red * (1 - protect), 1.5)
    L1 = L + (BG_L - L) * bg
    A1 = A * (1 - bg)
    B1 = B * (1 - bg)

    # 2) Vải trắng (váy, vest): trung tính, không phải da ấm, không phải mặt
    warm = ramp(B, 6, 12) * ramp(A, 3, 8)
    fabric = smooth(person * (1 - ramp(chroma, 9, 16)) * (1 - warm) * ramp(L, 50, 62) * (1 - faces), 1.2)
    Lf = L * 1.10                         # sáng theo tỉ lệ -> giữ nếp
    k = 88
    over = Lf > k
    Lf[over] = k + (100 - k) * np.tanh((Lf[over] - k) / (100 - k)) * 0.97   # không cháy trắng
    L1 = L1 * (1 - fabric) + Lf * fabric
    A1 = A1 * (1 - fabric * 0.7)
    B1 = B1 * (1 - fabric * 0.7)

    res = fromlab(np.dstack([L1, A1, B1]))
    # Chỉ ghép phần đã chỉnh; mặt, da, rèm, hoa giữ nguyên điểm ảnh gốc
    edit = np.clip(np.maximum(bg, fabric) * 1.5, 0, 1)[..., None]
    out = Image.fromarray((np.asarray(res) * edit + np.asarray(src) * (1 - edit)).round().astype("uint8"))
    out = out.crop((0, cfg["crop_top"], w, h))
    dst = os.path.join(IMG_DIR, cfg["out"])
    out.save(dst, "WEBP", quality=85, method=6)

    fm = faces[cfg["crop_top"]:] > 0.99
    diff = np.abs(np.asarray(out).astype(int) - np.asarray(src.crop((0, cfg["crop_top"], w, h))).astype(int)).max(axis=2)
    print(f"{name} -> {cfg['out']} {out.size} {os.path.getsize(dst) // 1024} KB, face diff: {int(diff[fm].max())}")


if __name__ == "__main__":
    names = sys.argv[1:] or list(PHOTOS)
    for n in names:
        process(n, PHOTOS[n])
