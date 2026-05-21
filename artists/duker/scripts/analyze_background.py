from PIL import Image
import numpy as np

frames = [0, 3, 6, 9, 12, 15]
img_data = {}

import os

script_dir = os.path.dirname(os.path.abspath(__file__))
artist_dir = os.path.dirname(script_dir)
sources_dir = os.path.join(artist_dir, "Sources_and_Assets")

for f in frames:
    path = os.path.join(sources_dir, f"frame_{f}.jpg")
    img = Image.open(path)
    img_data[f] = np.array(img)

# Print image sizes and color statistics
print("Frame dimensions:")
for f, arr in img_data.items():
    print(f"Frame {f}s: shape={arr.shape}")

# Let's inspect some standard region, e.g., the top part, middle part, and bottom part
print("\nColor analysis:")
# Average and standard deviation of colors for different frames
for f, arr in img_data.items():
    avg_color = arr.mean(axis=(0,1))
    std_color = arr.std(axis=(0,1))
    print(f"Frame {f}s: Average color={avg_color}, StdDev={std_color}")

# Let's check if the frames change at all, by computing the difference between subsequent frames
print("\nFrame differences (motion check):")
keys = list(img_data.keys())
for i in range(len(keys)-1):
    diff = np.abs(img_data[keys[i+1]].astype(float) - img_data[keys[i]].astype(float))
    mean_diff = diff.mean()
    max_diff = diff.max()
    print(f"Difference between {keys[i]}s and {keys[i+1]}s: Mean={mean_diff:.2f}, Max={max_diff:.2f}")

# Let's check if there is a black background or what parts are dark
print("\nDark pixel percentage (pixel value < 15):")
for f, arr in img_data.items():
    # Convert to grayscale for simple dark check
    gray = arr.mean(axis=2)
    dark_pct = (gray < 15).sum() / gray.size * 100
    print(f"Frame {f}s: {dark_pct:.2f}% of pixels are very dark/black")
