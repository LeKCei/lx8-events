# Promotional Video Design and Technical Proposals

This document provides visual, creative, and technical recommendations for the promotional videos of **Gui Boratto's 2026 Tour**. These suggestions are designed to maximize audience engagement on high-velocity social platforms like Instagram Reels, TikTok, and YouTube Shorts.

---

## 1. Visual Aesthetics & Composition

To maintain absolute brand consistency, the video should mirror the premium black-and-white art direction established in the high-resolution posters.

* **High-Contrast Monochromatic Palette**:
  * Keep the background video high-contrast black-and-white. If the source material is in color, apply a clean B&W saturation filter or a subtle silver-metallic tint.
  * Use solid white for primary typography, logos, and critical details.
* **Glassmorphism Overlay Card**:
  * Since promotional videos often have busy or highly dynamic backgrounds, use a semi-transparent, frosted-glass backdrop card to house the text.
  * **Technical Specs**: Apply a solid layer with a dark fill (`rgba(0, 0, 0, 0.72)`) and a subtle white border (`rgba(255, 255, 255, 0.1)`) with a blur radius (`backdrop-filter: blur(15px)`) in the center. This preserves the movement in the background while ensuring razor-sharp legibility.
* **Typography Hierarchy**:
  * **Artist Name**: Render `GUI BORATTO` in a bold, wide neo-grotesque sans-serif font (e.g., *Helvetica Neue Bold*, *Inter*, or *SF Pro Display*) at a prominent size.
  * **Sponsor/Host**: Use `DÜKER PRESENTS` or `dükermusic PRESENTS` in a smaller, tracked-out (wide letter-spacing) uppercase font above the name.
  * **Event/Tour Details**: Render dates and cities in a medium-weight sans-serif with clear columnar spacing.

---

## 2. Safe-Zone Configurations (Mobile Socials)

To prevent critical visual elements from being cropped or obscured by platform UI overlays (such as the account username, caption, like/share buttons, and profile icon), adhere to strict safe zones.

* **Top Margin (15% - 288px)**: Keep the top 288px of the 1080x1920 screen clear of essential text. This is where the platform's top header (e.g., "Following/For You" tabs) sits.
* **Bottom Margin (20% - 384px)**: Keep the bottom 384px free of primary text. This area is heavily obscured by captions, audio tags, and system interactions.
* **Sides (10% - 108px)**: Keep text elements at least 108px away from the left and right edges.
* **Optimal Layout Placement**:
  * Position the **Gui Boratto Logo** at the top center (around `y = 350px`).
  * Position the main **Tour Dates Grid** or **Show Info** in the middle center (between `y = 600px` and `y = 1450px`).
  * Position the solid white sponsor logos at the bottom center (around `y = 1500px` to `y = 1580px`).

---

## 3. Motion Graphics & Transitions

A dynamic, rhythm-driven video increases viewer retention by up to **40%**. We suggest the following kinetic behaviors:

* **Audio-Reactive Kick Pulse**:
  * Extract the kick drum transient (transient envelope) from the audio and use it to drive a subtle scale animation of the background video or the glassmorphism card (e.g., pulsing from `100%` to `102%` on every beat).
* **Kinetic Text Reveals**:
  * Instead of displaying all 16 tour dates statically for 18 seconds, split the schedule into **four logical groups of four dates** based on region:
    * **Group 1 (South America)**: São Paulo, Buenos Aires, Campinas.
    * **Group 2 (Europe Part 1)**: Basel, Ibiza, Lisbon.
    * **Group 3 (Europe Part 2 & UK)**: Barcelona, London, Paris, Amsterdam, Zurich, Munich.
    * **Group 4 (North & Central America)**: Tulum, Medellin, Juárez.
  * Animate these groups in sequence, with each group fading and sliding up onto the screen every **4 seconds** in sync with the musical phrasing.
* **Glow & Glitch Transitions**:
  * Apply a very fast, high-contrast glow transition (0.15s duration) at the moment the artist name appears or at major musical drops to emphasize energy.

---

## 4. Technical Audio/Video Specifications

For seamless playback and zero upload compression on Instagram, TikTok, and Shorts, use these exact export parameters:

| Parameter | Recommended Specification |
| :--- | :--- |
| **Video Codec** | H.264 (AVC) - High Profile @ Level 4.1 |
| **Container Format** | MP4 (`.mp4`) |
| **Resolution** | 1080 x 1920 px (Aspect Ratio 9:16) |
| **Frame Rate** | 30.0 fps (Constant Frame Rate) |
| **Target Video Bitrate** | 12 - 15 Mbps (Variable Bitrate, 2-Pass) |
| **Keyframe Interval** | 2 seconds (60 frames) |
| **Color Space** | Rec. 709 (sRGB standard) |
| **Audio Codec** | AAC-LC (Advanced Audio Coding - Low Complexity) |
| **Audio Bitrate** | 320 kbps (Stereo) |
| **Audio Sample Rate** | 44.1 kHz |

---

## 5. Soundtrack & Marketing Suggestions

* **Soundtrack Selection**:
  * Use one of Gui Boratto's iconic tracks to drive the promotional energy.
  * **Option 1**: *"Beautiful Life"* – Highly recognizable, uplifting, perfect for broad festival promo.
  * **Option 2**: *"No Turning Back"* – Melodic, deep, moody, matches the dark B&W visual aesthetic.
* **Targeted Ad Campaigns**:
  * Create regional cut-downs of the video (5 to 10 seconds long) showcasing *only* local dates. For example, serve the Europe version to users in Switzerland, Spain, Germany, and the UK, and the South America version to users in Brazil and Argentina. This drives significantly higher click-through rates.
* **Explicit Call-to-Action (CTA)**:
  * Include a final 3-second slate with a clear CTA: **"TICKETS ON SALE NOW - LINK IN BIO"** or **"GET TICKETS AT GUIBORATTO.COM"** in bold white text.
