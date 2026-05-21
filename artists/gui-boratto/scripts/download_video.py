import urllib.request
import os

fid = "1-fKdsDBqZ0V0XMuI1Oq7k8P8fR-Ovy_G"
name = "VIDEO-2025-05-08-17-54-08.mp4"
url = f"https://drive.google.com/uc?export=download&id={fid}"
script_dir = os.path.dirname(os.path.abspath(__file__))
artist_dir = os.path.dirname(script_dir)
sources_dir = os.path.join(artist_dir, "Sources_and_Assets")
dest = os.path.join(sources_dir, name)

print(f"Downloading {name}...")
try:
    urllib.request.urlretrieve(url, dest)
    print(f"Downloaded {name} successfully to {dest}")
except Exception as e:
    print(f"Failed to download {name}: {e}")
