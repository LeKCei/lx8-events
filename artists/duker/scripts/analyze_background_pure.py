from PIL import Image, ImageChops, ImageStat

frames = [0, 3, 6, 9, 12, 15]
images = {}

import os

script_dir = os.path.dirname(os.path.abspath(__file__))
artist_dir = os.path.dirname(script_dir)
sources_dir = os.path.join(artist_dir, "Sources_and_Assets")

for f in frames:
    path = os.path.join(sources_dir, f"frame_{f}.jpg")
    try:
        images[f] = Image.open(path)
    except Exception as e:
        print(f"Failed to open frame at {f}s: {e}")

print("Frame dimensions:")
for f, img in images.items():
    print(f"Frame {f}s: size={img.size}, mode={img.mode}")

print("\nColor and difference analysis:")
keys = list(images.keys())
for i in range(len(keys)-1):
    f1, f2 = keys[i], keys[i+1]
    if f1 in images and f2 in images:
        diff = ImageChops.difference(images[f1], images[f2])
        stat = ImageStat.Stat(diff)
        # stat.mean is a list of mean differences for each channel (R, G, B)
        # stat.extrema is a list of (min, max) differences for each channel
        print(f"Diff between {f1}s and {f2}s: Mean difference={stat.mean}, Extrema={stat.extrema}")
