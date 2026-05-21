import subprocess
import os
import shutil
import time

modes = ["tour", "event", "tour_sa", "tour_eu1", "tour_eu2", "tour_na"]
formats = ["story", "post"]
styles = ["gradient", "bokeh", "glass", "neon", "minimal"]

script_dir = os.path.dirname(os.path.abspath(__file__))
artist_dir = os.path.dirname(script_dir)  # grandparent of script, i.e., gui-boratto/

local_deliverables = os.path.join(artist_dir, "Final_Deliverables")
gdrive_deliverables = "/Users/alexei.ferreira/Google Drive/My Drive/guiboratto post/Final Deliverables"

executable = os.path.join(artist_dir, "src/video_editor")

os.makedirs(local_deliverables, exist_ok=True)

print("Starting batch rendering of all 60 video variations...")
start_time = time.time()

completed = 0
failed = []

for mode in modes:
    for fmt in formats:
        for style in styles:
            print(f"\n[{completed+1}/60] Rendering: mode={mode}, format={fmt}, style={style}...")
            run_start = time.time()
            
            cmd = [executable, mode, fmt, style]
            try:
                res = subprocess.run(cmd, capture_output=True, text=True, check=True)
                elapsed = time.time() - run_start
                print(f"[{completed+1}/60] SUCCESS in {elapsed:.2f}s")
                completed += 1
            except subprocess.CalledProcessError as e:
                print(f"[{completed+1}/60] FAILED: {e}")
                print(f"Error output:\n{e.stderr}")
                failed.append((mode, fmt, style))
                completed += 1

total_elapsed = time.time() - start_time
print("\n" + "="*50)
print(f"Batch rendering completed in {total_elapsed/60:.2f} minutes.")
print(f"Successfully rendered: {completed - len(failed)}/60")
if failed:
    print(f"Failed combinations: {failed}")
else:
    print("All combinations rendered successfully!")
print("="*50)

# Syncing to Google Drive
print("\nSyncing Final Deliverables to Google Drive...")
gdrive_targets = [
    "/Users/alexei.ferreira/Google Drive/My Drive/guiboratto post/Final Deliverables",
    "/Users/alexei.ferreira/Google Drive/My Drive/Gui Boratto Events/Final Deliverables"
]

for target in gdrive_targets:
    try:
        print(f"Syncing to target: {target}")
        if os.path.exists(target):
            shutil.rmtree(target)
        shutil.copytree(local_deliverables, target)
        print(f"Sync to {target} completed successfully!")
    except Exception as e:
        print(f"Error syncing to {target}: {e}")

