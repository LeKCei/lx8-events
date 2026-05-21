import subprocess
import os
import shutil
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

modes = ["tour", "event", "tour_sa", "tour_eu1", "tour_eu2", "tour_na"]
formats = ["story", "post"]
styles = ["gradient", "bokeh", "glass", "neon", "minimal"]

script_dir = os.path.dirname(os.path.abspath(__file__))
artist_dir = os.path.dirname(script_dir)  # grandparent of script, i.e., gui-boratto/

local_deliverables = os.path.join(artist_dir, "Final_Deliverables")
executable = os.path.join(artist_dir, "src/video_editor")

os.makedirs(local_deliverables, exist_ok=True)

def render_single_video(args):
    mode, fmt, style = args
    cmd = [executable, mode, fmt, style]
    run_start = time.time()
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        elapsed = time.time() - run_start
        return (mode, fmt, style, True, elapsed, "")
    except subprocess.CalledProcessError as e:
        elapsed = time.time() - run_start
        return (mode, fmt, style, False, elapsed, e.stderr)

def main():
    tasks = []
    for mode in modes:
        for fmt in formats:
            for style in styles:
                tasks.append((mode, fmt, style))
                
    total_tasks = len(tasks)
    print(f"Starting parallel batch rendering of all {total_tasks} video variations using 6 parallel workers...")
    start_time = time.time()
    
    completed = 0
    failed = []
    
    with ProcessPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(render_single_video, t): t for t in tasks}
        for future in as_completed(futures):
            mode, fmt, style, success, elapsed, err_msg = future.result()
            completed += 1
            if success:
                print(f"[{completed}/{total_tasks}] SUCCESS: mode={mode}, format={fmt}, style={style} in {elapsed:.2f}s")
            else:
                print(f"[{completed}/{total_tasks}] FAILED: mode={mode}, format={fmt}, style={style} in {elapsed:.2f}s")
                print(f"Error output:\n{err_msg}")
                failed.append((mode, fmt, style))
                
    total_elapsed = time.time() - start_time
    print("\n" + "="*50)
    print(f"Parallel batch rendering completed in {total_elapsed/60:.2f} minutes.")
    print(f"Successfully rendered: {completed - len(failed)}/{total_tasks}")
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

if __name__ == "__main__":
    main()
