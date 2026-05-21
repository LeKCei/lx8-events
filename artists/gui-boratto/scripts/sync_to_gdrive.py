import os
import shutil

script_dir = os.path.dirname(os.path.abspath(__file__))
artist_dir = os.path.dirname(script_dir)

local_deliverables = os.path.join(artist_dir, "Final_Deliverables")
local_sources = os.path.join(artist_dir, "Sources_and_Assets")

gdrive_targets = [
    "/Users/alexei.ferreira/Google Drive/My Drive/guiboratto post",
    "/Users/alexei.ferreira/Google Drive/My Drive/Gui Boratto Events"
]

print("=== Starting Google Drive Sync & Cleanup ===")

# Verify local files first
if not os.path.exists(local_deliverables):
    print(f"Error: Local deliverables path {local_deliverables} does not exist.")
    exit(1)

print("\nLocal final deliverables structure:")
for root, dirs, files in os.walk(local_deliverables):
    level = root.replace(local_deliverables, '').count(os.sep)
    indent = ' ' * 4 * (level)
    print(f"{indent}{os.path.basename(root)}/ ({len(files)} files)")

for target in gdrive_targets:
    print("\n" + "="*50)
    print(f"Processing Google Drive Target: {target}")
    
    gdrive_deliv_path = os.path.join(target, "Final Deliverables")
    gdrive_sources_path = os.path.join(target, "Sources & Assets")
    
    # 1. Verify and protect Sources & Assets (don't delete anything, keep old photos)
    print("\n[1/3] Checking Sources & Assets (Preserving Old Photos)...")
    if os.path.exists(gdrive_sources_path):
        old_photos = ["gui boratto_edit_pb--11.JPEG", "reference.JPG"]
        found_old_photos = []
        for file in os.listdir(gdrive_sources_path):
            if file in old_photos:
                found_old_photos.append(file)
        print(f"Found old photos to preserve: {found_old_photos}")
        print(f"Total files in Sources & Assets: {len(os.listdir(gdrive_sources_path))}")
    else:
        print(f"Sources & Assets not found in target, copying from local...")
        shutil.copytree(local_sources, gdrive_sources_path)
        print("Sources & Assets copied successfully!")
        
    # 2. Cleanup Final Deliverables (remove all old/broken videos)
    print("\n[2/3] Cleaning up broken/old videos from Final Deliverables...")
    if os.path.exists(gdrive_deliv_path):
        print(f"Removing existing Final Deliverables at: {gdrive_deliv_path}")
        shutil.rmtree(gdrive_deliv_path)
    
    # 3. Copy new color videos and new photos (posters) from local Final_Deliverables
    print("\n[3/3] Syncing new color videos and new photos...")
    shutil.copytree(local_deliverables, gdrive_deliv_path)
    print("New videos and photos copied successfully!")
    
    # Verify sync results
    print("\nVerification for target:")
    for root, dirs, files in os.walk(gdrive_deliv_path):
        level = root.replace(gdrive_deliv_path, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f"{indent}{os.path.basename(root)}/ ({len(files)} files)")

print("\n" + "="*50)
print("Sync & Cleanup process finished successfully!")
