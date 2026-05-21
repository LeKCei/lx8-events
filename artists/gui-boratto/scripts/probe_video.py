import subprocess
import shutil
import sys

import os

script_dir = os.path.dirname(os.path.abspath(__file__))
artist_dir = os.path.dirname(script_dir)
video_path = os.path.join(artist_dir, "Sources_and_Assets", "VIDEO-2025-05-08-17-54-08.mp4")

print("System details:")
print("Python version:", sys.version)

ffmpeg_path = shutil.which("ffmpeg")
ffprobe_path = shutil.which("ffprobe")
print("ffmpeg path:", ffmpeg_path)
print("ffprobe path:", ffprobe_path)

# Try importing opencv or other libraries
try:
    import cv2
    print("OpenCV is installed. Version:", cv2.__version__)
except ImportError:
    print("OpenCV is NOT installed.")

try:
    import PIL
    print("Pillow is installed. Version:", PIL.__version__)
except ImportError:
    print("Pillow is NOT installed.")

# Use ffprobe to get video info if available
if ffprobe_path:
    print("\nProbing video with ffprobe:")
    cmd = [
        ffprobe_path,
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,duration,r_frame_rate,codec_name",
        "-of", "default=noprint_wrappers=1",
        video_path
    ]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        print(res.stdout)
    except Exception as e:
        print("ffprobe failed:", e)
else:
    print("ffprobe is not available, cannot probe video details automatically.")
