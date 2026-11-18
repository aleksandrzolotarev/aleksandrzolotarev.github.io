import json, os, re
files = {}
for d in sorted(os.listdir("photos")) if os.path.isdir("photos") else []:
    p = os.path.join("photos", d)
    if not os.path.isdir(p):
        continue
    key = re.sub(r"[\s_-]", "", d.lower())
    for f in os.listdir(p):
        if re.search(r"\.(jpe?g|png|webp)$", f, re.I):
            files.setdefault(key, []).append(d + "/" + f)
for k in files:
    files[k].sort()
with open("photos.json", "w") as fh:
    json.dump(files, fh, ensure_ascii=False, indent=1)
print({k: len(v) for k, v in files.items()})
