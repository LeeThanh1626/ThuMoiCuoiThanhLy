"""2W4A4766.jpg -> album-04.webp
- Nền (tường be, sàn gỗ) -> trắng
- Váy / áo vest trắng: sáng hơn, giữ nếp vải
- KHÔNG nâng sáng toàn ảnh, KHÔNG đụng vào mặt và da
"""
import os
import numpy as np
from PIL import Image, ImageOps, ImageCms, ImageFilter

os.chdir(os.path.dirname(os.path.abspath(__file__)))

srgb = ImageCms.createProfile('sRGB')
lab = ImageCms.createProfile('LAB')
to_lab = ImageCms.buildTransformFromOpenProfiles(srgb, lab, 'RGB', 'LAB')
to_rgb = ImageCms.buildTransformFromOpenProfiles(lab, srgb, 'LAB', 'RGB')


def tolab(im):
    x = np.asarray(ImageCms.applyTransform(im, to_lab))
    return np.dstack([x[..., 0].astype(float) / 255 * 100,
                      x[..., 1:].copy().view(np.int8).astype(float)])


def fromlab(x):
    L = np.clip(x[..., 0] / 100 * 255, 0, 255).round().astype(np.uint8)
    ab = np.clip(x[..., 1:], -128, 127).round().astype(np.int8).view(np.uint8)
    return ImageCms.applyTransform(Image.fromarray(np.dstack([L, ab]), 'LAB'), to_rgb)


def smooth(m, r):
    return np.asarray(Image.fromarray((np.clip(m, 0, 1) * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(r))).astype(float) / 255


def ramp(v, lo, hi):
    return np.clip((v - lo) / (hi - lo), 0, 1)


src = ImageOps.exif_transpose(Image.open('assets/img/2W4A4766.jpg')).convert('RGB')
src = src.resize((934, round(src.height * 934 / src.width)), Image.LANCZOS)
x = tolab(src)
L, A, B = x[..., 0], x[..., 1], x[..., 2]
h, w = L.shape
chroma = np.hypot(A, B)
yy, xx = np.mgrid[0:h, 0:w]
sx, sy = w / 862, h / 1292  # toạ độ tham chiếu theo ảnh xem trước 862px


def box(x0, y0, x1, y1):
    return ((xx >= x0 * sx) & (xx < x1 * sx) & (yy >= y0 * sy) & (yy < y1 * sy)).astype(float)


person = smooth(np.maximum(box(205, 325, 585, 1062), box(340, 760, 752, 1062)), 6)
# Mặt + cổ hai người: tuyệt đối không chỉnh
faces = smooth(np.maximum(box(285, 330, 390, 470), box(425, 370, 520, 500)), 4)

# --- 1) Nền -> trắng (chỉ trong vùng tường/sàn, chừa màu đỏ)
wall = np.maximum(box(0, 0, 160, 620), box(706, 0, 934, 620))
floor = np.maximum(box(0, 940, 175, 1292), box(680, 950, 934, 1292))
not_red = (1 - ramp(A, 18, 28)) * (1 - ramp(chroma, 22, 32))
bg = wall * ramp(L, 32, 42) + floor * ramp(L, 8, 16)
protect = person * np.maximum(1 - floor, ramp(L, 62, 72))
bg = smooth(np.clip(bg, 0, 1) * not_red * (1 - protect), 1.5)
WHITE_L = 95
L1 = L + (WHITE_L - L) * bg
A1 = A * (1 - bg)
B1 = B * (1 - bg)

# --- 2) Váy + vest trắng: vải trung tính (không phải da ấm), đủ sáng
warm = ramp(B, 6, 12) * ramp(A, 3, 8)            # da: a,b dương -> loại ra
fabric = person * (1 - ramp(chroma, 9, 16)) * (1 - warm) * ramp(L, 50, 62) * (1 - faces)
fabric = smooth(fabric, 1.2)
# Sáng hơn theo tỉ lệ (giữ nguyên tỉ lệ sáng/tối giữa các nếp), rồi cuộn mềm vùng sáng nhất để không cháy
gain = 1.10
Lf = L * gain
k = 88
over = Lf > k
Lf[over] = k + (100 - k) * np.tanh((Lf[over] - k) / (100 - k)) * 0.97
L1 = L1 * (1 - fabric) + Lf * fabric
# Bỏ ám vàng/xám trên vải, trắng sạch
A1 = A1 * (1 - fabric * 0.7)
B1 = B1 * (1 - fabric * 0.7)

res = fromlab(np.dstack([L1, A1, B1]))
# Chỉ lấy phần đã chỉnh (nền + vải); mọi chỗ khác (mặt, da, rèm, hoa) giữ nguyên điểm ảnh gốc
edit = np.clip(np.maximum(bg, fabric) * 1.5, 0, 1)[..., None]
res = Image.fromarray((np.asarray(res) * edit + np.asarray(src) * (1 - edit)).round().astype('uint8'))
res = res.crop((0, 24, res.width, res.height))   # bỏ dải tối sát mép trên ảnh gốc
res.save('assets/img/album-04.webp', 'WEBP', quality=85, method=6)
print(res.size, os.path.getsize('assets/img/album-04.webp') // 1024, 'KB')
