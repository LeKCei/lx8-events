# 🎥 LX8 Events Creative Engine

Welcome to the **LX8 Events Creative Engine**—a premium, high-performance, automated media rendering and asset synchronization pipeline designed for electronic music events, tours, and artist campaigns.

This repository serves as a centralized, scalable, and machine-independent system to generate high-fidelity, audio-reactive promo videos, high-resolution posters, and sync assets directly to cloud storage platforms like Google Drive.

---

## 🏗️ Repository Architecture

The workspace is structured using a clean, scalable modular design. Each artist or campaign has its own self-contained directory containing its specific assets, templates, source video/audio, and custom pipelines.

```
lx8-events/
├── .gitignore
├── README.md
└── artists/
    └── gui-boratto/
        ├── tour_dates.csv             # The source of truth for tour stops
        ├── Sources_and_Assets/        # Raw logos, background footage, and reference photos
        ├── Final_Deliverables/        # Auto-generated high-fidelity video and image assets
        │   ├── Instagram_Posts_4_5/
        │   └── Instagram_Stories_Reels_9_16/
        ├── src/                       # Swift rendering engine source code
        │   ├── video_editor.swift     # Core AVFoundation rendering pipeline
        │   └── [auxiliary_scripts].swift
        └── scripts/                   # Python automation tools
            ├── render_all_videos.py   # Batch-renders all 60 style combinations
            ├── sync_to_gdrive.py      # Cleans up and syncs deliverables to Google Drive
            ├── generate_posters.py    # Generates high-res social poster graphics
            └── [utilities].py
```

---

## ⚡ Core Technologies

### 1. High-Performance Swift AVFoundation Engine
At the heart of the campaign is a custom Swift-based video rendering engine (`video_editor.swift`) that interfaces directly with macOS hardware-accelerated **AVFoundation** and **CoreGraphics** APIs. 
* **Dynamic Content Overlay**: Dynamically parses `tour_dates.csv` and compiles rich text layouts directly onto the video.
* **Audio-Reactive Beats**: Implements a kick-reactive pulse animation (calculated on beat-intervals based on track BPM) that pumps the scale and opacity of assets dynamically.
* **Multi-Format Output**: Automatically scales and formats layouts for both **Instagram Posts (4:5)** and **Instagram Stories/Reels/TikTok (9:16)**.
* **Custom Styling Presets**: Supports modular, stunning graphical treatments including:
  * `gradient` (vibrant, modern color flows)
  * `bokeh` (premium out-of-focus background light-bursts)
  * `glass` (frosted glass glassmorphism panels)
  * `neon` (electric neon glows)
  * `minimal` (sleek, high-contrast typography)

### 2. Python Automation & GDrive Synchronization Pipeline
A suite of Python scripts automates the high-volume creation and distribution:
* **Batch Production**: `render_all_videos.py` orchestrates the rendering of all 60 combinations of tour segments, aspect ratios, and design styles in minutes.
* **Automated Cloud Sync**: `sync_to_gdrive.py` performs differential synchronizations to Google Drive folders, protecting and preserving historical archives while delivering pristine new video sets to target shared drives.

---

## 🚀 Quick Start Guide

### 1. Compile the Swift Engine
First, compile the Swift video renderer on macOS:
```bash
swiftc -O artists/gui-boratto/src/video_editor.swift -o artists/gui-boratto/src/video_editor
```

### 2. Render a Single Video Variant
Execute the compiled binary with command-line arguments to render a custom video:
```bash
./artists/gui-boratto/src/video_editor [mode] [format] [style]
```
* **Modes**: `tour`, `event`, `tour_sa`, `tour_eu1`, `tour_eu2`, `tour_na`
* **Formats**: `story`, `post`
* **Styles**: `gradient`, `bokeh`, `glass`, `neon`, `minimal`

*Example:*
```bash
./artists/gui-boratto/src/video_editor tour story neon
```

### 3. Run the Batch Production & Sync
To render all 60 variations and upload them to active Google Drive shares in one step:
```bash
python3 artists/gui-boratto/scripts/render_all_videos.py
```

---

## 📈 Scaling for Future Artists

To add a new artist (e.g. `stephan-bodzin`), simply duplicate the folder structure under `artists/`:
1. Create `artists/stephan-bodzin/`.
2. Place their raw assets under `Sources_and_Assets/`.
3. Add their specific dates in `tour_dates.csv`.
4. Compile the engine inside their folder, customize styling if needed, and execute!

---

*Engineered with 🖤 for LX8 Events.*
