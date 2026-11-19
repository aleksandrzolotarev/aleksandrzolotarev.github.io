"""Build photos.json and light copies of every photo.

photos/<album>/<file>  original uploaded by Aleksandr (never changed)
thumbs/<album>/<file>  small copy for the gallery grid (480 px wide)
large/<album>/<file>   medium copy for full-screen view (max 1600 px)
"""
import json, os, re

from PIL import Image, ImageOps

EXT = re.compile(r"\.(jpe?g|png|webp)$", re.I)
SIZES = {"thumbs": ("width", 480, 72), "large": ("box", 1600, 80)}


def natural(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]


def make_copy(src, dst, mode, size, quality):
    if os.path.exists(dst):
        return False
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
        if mode == "width":
            if im.width > size:
                im = im.resize((size, round(im.height * size / im.width)), Image.LANCZOS)
        else:
            im.thumbnail((size, size), Image.LANCZOS)
        im.save(dst, "JPEG", quality=quality, optimize=True, progressive=True)
    return True


files, wanted, made = {}, set(), 0
for d in sorted(os.listdir("photos")) if os.path.isdir("photos") else []:
    p = os.path.join("photos", d)
    if not os.path.isdir(p):
        continue
    key = re.sub(r"[\s_-]", "", d.lower())
    for f in os.listdir(p):
        if not EXT.search(f):
            continue
        files.setdefault(key, []).append(d + "/" + f)
        out_name = re.sub(EXT, ".jpg", f)
        for folder, (mode, size, q) in SIZES.items():
            dst = os.path.join(folder, d, out_name)
            wanted.add(dst)
            made += make_copy(os.path.join(p, f), dst, mode, size, q)

# remove copies whose original was deleted
for folder in SIZES:
    for root, _, names in os.walk(folder):
        for n in names:
            path = os.path.join(root, n)
            if path not in wanted:
                os.remove(path)

for k in files:
    files[k].sort(key=natural)
with open("photos.json", "w") as fh:
    json.dump(files, fh, ensure_ascii=False, indent=1)
print({k: len(v) for k, v in files.items()}, "new copies:", made)
