"""Pass 2: further reduce WebP sizes.
- Backgrounds (mờ/overlay): max 900px, quality 65
- Foreground (gallery, hero, profile): max 1100px, quality 75
"""
import os
from PIL import Image

SRC_DIR = "assets/img"

# Background images that are blurred/at low opacity in HTML
BG_IMAGES = {
    "bg.jpg", "bg2.jpg",  # home section bg (25% opacity) + profile circle (kept reasonable)
    "ab1.jpg", "ab2.jpg", "ab3.jpg",  # desktop slides (60% opacity)
}
# Wave separators and gallery/hero are foreground - keep higher quality
# Default everything else to foreground

def optimize(fname, max_dim, quality):
    src = os.path.join(SRC_DIR, fname)
    name_no_ext = os.path.splitext(fname)[0]
    dst = os.path.join(SRC_DIR, name_no_ext + ".webp")
    size_before = os.path.getsize(src)

    with Image.open(src) as img:
        img = img.convert("RGB")
        w, h = img.size
        scale = min(max_dim / w, max_dim / h, 1.0)
        if scale < 1.0:
            img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        img.save(dst, "WEBP", quality=quality, method=6)

    size_after = os.path.getsize(dst)
    return size_before, size_after

total_before = 0
total_after = 0

for fname in sorted(os.listdir(SRC_DIR)):
    if not fname.lower().endswith((".jpg", ".jpeg")):
        continue

    if fname in BG_IMAGES:
        max_dim, quality, kind = 900, 65, "bg "
    else:
        max_dim, quality, kind = 1100, 75, "fg "

    sb, sa = optimize(fname, max_dim, quality)
    total_before += sb
    total_after += sa
    print(f"[{kind}] {fname:15} {sb/1024/1024:5.1f}MB -> {sa/1024:6.1f}KB  "
          f"(q={quality} max={max_dim}px)")

print(f"\nTOTAL: {total_before/1024/1024:.1f}MB -> {total_after/1024:.1f}KB "
      f"({total_after/1024/1024:.2f}MB, saved {(1-total_after/total_before)*100:.1f}%)")
