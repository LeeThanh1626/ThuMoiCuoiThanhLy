"""NUU_8067.JPG -> album-ngang-06.webp
- Cắt (zoom) theo khung ảnh mẫu: tỉ lệ 2000x1031, cặp đôi lệch trái giữa, chân sát mép dưới
- Kéo dài chân ~7%: giãn phần dưới eo theo chiều dọc, chuyển tiếp mượt (không có đường nối)
"""
import os
import numpy as np
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "assets", "img", "NUU_8067.JPG")
DST = os.path.join(ROOT, "assets", "img", "album-ngang-06.webp")

OUT_W, OUT_H = 2000, 1031
# Toạ độ theo ảnh thu nhỏ rộng 1200px
CROP_LEFT, CROP_RIGHT = 117, 1076
WAIST_Y = 548        # ngang eo cô dâu/chú rể
FEET_Y = 657         # gót chân
LEG_STRETCH = 1.07   # chân dài thêm 7%
BLEND = 25           # độ dài vùng chuyển tiếp (px ảnh 1200)
FEET_AT = 0.975      # vị trí gót chân trong ảnh ra (tỉ lệ chiều cao)


def main():
    im = ImageOps.exif_transpose(Image.open(SRC)).convert("RGB")
    k = im.width / 1200
    a = np.asarray(im).astype(np.float32)
    H = a.shape[0]

    x0, x1 = round(CROP_LEFT * k), round(CROP_RIGHT * k)
    crop_w = x1 - x0
    crop_h = round(crop_w * OUT_H / OUT_W)
    waist, feet, blend = WAIST_Y * k, FEET_Y * k, BLEND * k

    # Hàm ánh xạ toạ độ ra -> toạ độ nguồn. Mật độ = 1 phía trên eo, 1/LEG_STRETCH phía dưới (chuyển mượt)
    # Tính trước bảng y_src theo y_out (tính từ 0 = đỉnh ảnh nguồn)
    ys_out = np.arange(0, round(H * LEG_STRETCH) + 1, dtype=np.float64)
    t = np.clip((ys_out - waist) / blend, 0, 1)
    t = t * t * (3 - 2 * t)                       # smoothstep
    dens = 1 - (1 - 1 / LEG_STRETCH) * t
    y_src = np.concatenate([[0], np.cumsum(dens[:-1])])

    # Vị trí gót chân sau khi giãn -> chọn đỉnh khung sao cho gót ở FEET_AT
    feet_out = np.interp(feet, y_src, ys_out)
    top_out = feet_out - FEET_AT * crop_h
    rows_out = top_out + np.arange(crop_h)
    rows_src = np.clip(np.interp(rows_out, ys_out, y_src), 0, H - 1)

    r0 = np.floor(rows_src).astype(int)
    r1 = np.minimum(r0 + 1, H - 1)
    f = (rows_src - r0)[:, None, None]
    region = a[:, x0:x1]
    out = region[r0] * (1 - f) + region[r1] * f

    img = Image.fromarray(np.clip(out, 0, 255).round().astype(np.uint8))
    img = img.resize((OUT_W, OUT_H), Image.LANCZOS)
    img.save(DST, "WEBP", quality=86, method=6)
    print(os.path.basename(DST), img.size, os.path.getsize(DST) // 1024, "KB",
          "| crop src", (x0, round(rows_src[0]), x1, round(rows_src[-1])))


if __name__ == "__main__":
    main()
