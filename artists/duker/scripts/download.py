import urllib.request
import os

files = {
    "gui boratto_edit_pb--11.JPEG": "11Xsf_nCVbmO2EQElEe58gQRrEcUWj4b1",
    "metropole logo.png": "1GARzQGr-PtbRaoILFWzpWXNM2TUKS7rd",
    "dukermusic_logo_white.PNG": "1hTZ0Z-CzZd7iewe1b8HWmTqdtDSI0nwD",
    "reference.JPG": "19deuLvjkx6yqGybAbr8uLuTuf3W_A7iy",
    "DOC_AVATAR6.PNG": "1WiXDn5BAu8He5XJV2GGCwDQlkTPGVHVk",
    "gui boratto logo.svg": "1YZiOQ2Fpa8FoUewM1sX6RvXqRpQ8wfSQ",
    "cf99ade3-9b45-4736-b77b-c7c36707688f.JPG": "1FZ84NxCrBy2ZuJbU1NI4uNxGyBPr47-b",
    "tour dates.csv": "1Qd0yGCuCHKRj6EgPlf0RS_J5l0rGPq8i",
}

script_dir = os.path.dirname(os.path.abspath(__file__))
artist_dir = os.path.dirname(script_dir)
sources_dir = os.path.join(artist_dir, "Sources_and_Assets")

os.makedirs(sources_dir, exist_ok=True)

for name, fid in files.items():
    url = f"https://drive.google.com/uc?export=download&id={fid}"
    dest = os.path.join(sources_dir, name)
    print(f"Downloading {name}...")
    try:
        urllib.request.urlretrieve(url, dest)
        print(f"Downloaded {name} successfully.")
    except Exception as e:
        print(f"Failed to download {name}: {e}")
