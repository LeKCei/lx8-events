import os
import sys
import json
import shutil
import subprocess
import urllib.parse
from http.server import BaseHTTPRequestHandler
from socketserver import ThreadingTCPServer

PORT = 8080
WORKSPACE_DIR = "/Users/alexei.ferreira/Events"

# Static geocoding mapping for 3D Globe Projection
GEOLOCATIONS = {
    "sao paulo": [-23.5505, -46.6333],
    "buenos aires": [-34.6037, -58.3816],
    "basel": [47.5596, 7.5886],
    "ibiza": [38.9067, 1.4206],
    "lisbon": [38.7223, -9.1393],
    "barcelona": [41.3851, 2.1734],
    "costa da caparica": [38.6430, -9.2312],
    "zurich": [47.3769, 8.5417],
    "munich": [48.1351, 11.5820],
    "london": [51.5074, -0.1278],
    "tulum": [20.2114, -87.4654],
    "medellin": [6.2442, -75.5812],
    "juarez": [31.6904, -106.4245],
    "paris": [48.8566, 2.3522],
    "amsterdam": [52.3676, 4.9041],
    "campinas": [-22.9099, -47.0626],
    "berlin": [52.5200, 13.4050],
}

def get_coordinates(city_name):
    c = city_name.lower().strip()
    # Direct match check
    for key, val in GEOLOCATIONS.items():
        if key in c or c in key:
            return val
    # Semi-deterministic fallback for offline reliability
    h = hash(c)
    lat = (h % 80) - 40
    lng = ((h // 10) % 320) - 160
    return [lat, lng]

def load_tour_dates(artist_id):
    csv_path = os.path.join(WORKSPACE_DIR, "artists", artist_id, "tour_dates.csv")
    dates = []
    if os.path.exists(csv_path):
        with open(csv_path, "r", encoding="utf-8") as f:
            for line in f:
                trimmed = line.strip()
                if not trimmed or trimmed.startswith("#"):
                    continue
                parts = trimmed.split(",")
                if len(parts) >= 4:
                    city = parts[2].strip()
                    coords = get_coordinates(city)
                    dates.append({
                        "date": parts[0].strip(),
                        "venue": parts[1].strip(),
                        "city": city,
                        "country": parts[3].strip(),
                        "lat": coords[0],
                        "lng": coords[1]
                    })
    return dates

def get_artist_metadata(artist_id):
    metadata_path = os.path.join(WORKSPACE_DIR, "artists", artist_id, "artist.json")
    metadata = {}
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
        except Exception:
            pass
    if not metadata:
        name = artist_id.replace("-", " ").title()
        metadata = {
            "id": artist_id,
            "name": name,
            "sub": "Techno / House Producer",
            "bio": f"Artist {name} curated by LX8 Events.",
            "avatar": "".join([w[0] for w in name.split() if w])[:2].upper(),
            "avatarClass": "gui" if "gui" in artist_id else "duker",
            "redirect": f"LINK IN BIO - {artist_id.upper().replace('-', '')}.COM",
            "web_title": f"{name} | Official Web Portal",
            "web_description": f"Official tour dates, audio reels, and electronic press kit for {name}.",
            "spotify_embed": "https://open.spotify.com/embed/track/3b5uT21XJ8J8Fk72412v6Z",
            "bpm": 124,
            "web_theme": "glass",
            "mesh_color": "classic"
        }
    
    # Ensure default values exist
    defaults = {
        "web_title": f"{metadata.get('name', 'Artist')} | Official Web Portal",
        "web_description": "Official tour dates, audio reels, and electronic press kit.",
        "spotify_embed": "https://open.spotify.com/embed/track/3b5uT21XJ8J8Fk72412v6Z",
        "bpm": 124,
        "web_theme": "glass",
        "mesh_color": "classic"
    }
    for k, v in defaults.items():
        if k not in metadata:
            metadata[k] = v
            
    metadata["dates"] = load_tour_dates(artist_id)
    return metadata

# -------------------------------------------------------------
# HIGH-FIDELITY WEB PORTAL COMPILER (HTML TEMPLATE GENERATOR)
# -------------------------------------------------------------
def build_html_template(artist_metadata, preview_mode=False):
    art = artist_metadata
    bpm = int(art.get("bpm", 124))
    pulse_duration = 60.0 / bpm
    
    # Select mesh gradient style
    mesh_map = {
        "classic": "radial-gradient(circle at 10% 20%, rgba(18, 9, 46, 0.9) 0%, rgba(9, 26, 46, 0.9) 40%, rgba(30, 8, 28, 0.9) 100%)",
        "emerald": "radial-gradient(circle at 15% 15%, rgba(4, 31, 23, 0.9) 0%, rgba(9, 14, 26, 0.9) 50%, rgba(10, 29, 36, 0.9) 100%)",
        "cyberpunk": "radial-gradient(circle at 80% 20%, rgba(48, 8, 38, 0.9) 0%, rgba(9, 10, 28, 0.9) 45%, rgba(12, 34, 46, 0.9) 100%)",
        "cyan": "radial-gradient(circle at 30% 70%, rgba(8, 42, 54, 0.9) 0%, rgba(7, 12, 31, 0.9) 50%, rgba(28, 10, 41, 0.9) 100%)"
    }
    gradient = mesh_map.get(art.get("mesh_color", "classic"), mesh_map["classic"])
    
    # Accent color
    accent_map = {
        "classic": "#af40ff",
        "emerald": "#00ffaa",
        "cyberpunk": "#ff007f",
        "cyan": "#00f3ff"
    }
    accent_color = accent_map.get(art.get("mesh_color", "classic"), accent_map["classic"])

    # Build tour points array for JS Canvas globe
    dates_json = json.dumps(art.get("dates", []))

    # Output premium website
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{art.get("web_description")}">
    <title>{art.get("web_title")}</title>
    
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;600;800&family=Syne:wght@700;800&display=swap" rel="stylesheet">
    
    <style>
        :root {{
            --bg-mesh: {gradient};
            --accent-color: {accent_color};
            --pulse-dur: {pulse_duration:.3f}s;
            --glass-bg: rgba(18, 16, 28, 0.55);
            --glass-border: rgba(255, 255, 255, 0.08);
            --text-primary: #f3f3f7;
            --text-secondary: #a09eb5;
            --font-ui: 'Inter', sans-serif;
            --font-brand: 'Outfit', sans-serif;
            --font-display: 'Syne', sans-serif;
        }}
        
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            font-family: var(--font-ui);
            background: var(--bg-mesh);
            color: var(--text-primary);
            min-height: 100vh;
            overflow-x: hidden;
            line-height: 1.6;
        }}
        
        /* Premium Moving Mesh Animation */
        @keyframes meshMove {{
            0% {{ background-position: 0% 50% }}
            50% {{ background-position: 100% 50% }}
            100% {{ background-position: 0% 50% }}
        }}
        
        /* Beat Synced Pulsation */
        @keyframes beatPulse {{
            0%, 100% {{ transform: scale(1); box-shadow: 0 0 15px rgba(255, 255, 255, 0.05); }}
            50% {{ transform: scale(1.02); box-shadow: 0 0 30px var(--accent-color); border-color: var(--accent-color); }}
        }}
        
        .pulse-card {{
            animation: beatPulse var(--pulse-dur) infinite ease-in-out;
        }}
        
        /* Glassmorphic elements */
        .glass-header {{
            background: rgba(10, 8, 18, 0.6);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid var(--glass-border);
            position: sticky;
            top: 0;
            z-index: 100;
            padding: 20px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .brand-logo {{
            font-family: var(--font-brand);
            font-weight: 800;
            font-size: 1.5rem;
            color: #fff;
            text-decoration: none;
            letter-spacing: 2px;
        }}
        
        .brand-logo span {{
            color: var(--accent-color);
        }}
        
        .nav-links {{
            display: flex;
            gap: 30px;
            list-style: none;
        }}
        
        .nav-links a {{
            color: var(--text-secondary);
            text-decoration: none;
            font-weight: 500;
            font-size: 0.95rem;
            transition: all 0.3s ease;
        }}
        
        .nav-links a:hover {{
            color: #fff;
            text-shadow: 0 0 10px var(--accent-color);
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 60px 20px;
        }}
        
        .hero {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 60px;
            margin-bottom: 80px;
        }}
        
        @media(max-width: 900px) {{
            .hero {{
                flex-direction: column;
                text-align: center;
            }}
        }}
        
        .hero-text {{
            flex: 1;
        }}
        
        .hero-title {{
            font-family: var(--font-display);
            font-size: 4rem;
            font-weight: 800;
            line-height: 1.1;
            margin-bottom: 20px;
            letter-spacing: -1px;
        }}
        
        .hero-subtitle {{
            font-family: var(--font-brand);
            color: var(--accent-color);
            font-size: 1.5rem;
            margin-bottom: 20px;
            font-weight: 600;
        }}
        
        .hero-bio {{
            color: var(--text-secondary);
            font-size: 1.1rem;
            margin-bottom: 30px;
        }}
        
        .hero-visuals {{
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
        }}
        
        /* Interactive Globe Canvas Styling */
        .globe-container {{
            width: 360px;
            height: 360px;
            position: relative;
            background: rgba(18, 16, 28, 0.3);
            border-radius: 50%;
            border: 1px solid var(--glass-border);
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: hidden;
        }}
        
        #tour-globe {{
            cursor: grab;
            width: 100%;
            height: 100%;
        }}
        
        .globe-tooltip {{
            position: absolute;
            background: rgba(10, 8, 18, 0.9);
            border: 1px solid var(--accent-color);
            padding: 8px 14px;
            border-radius: 8px;
            font-size: 0.85rem;
            pointer-events: none;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
            display: none;
            z-index: 10;
        }}
        
        /* Cards & Grids */
        .grid-2 {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
            margin-bottom: 80px;
        }}
        
        @media(max-width: 800px) {{
            .grid-2 {{
                grid-template-columns: 1fr;
            }}
        }}
        
        .glass-card {{
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 20px;
            padding: 40px;
            backdrop-filter: blur(20px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.25);
            transition: all 0.3s ease;
        }}
        
        .glass-card:hover {{
            border-color: rgba(255,255,255,0.12);
        }}
        
        .section-title {{
            font-family: var(--font-brand);
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 30px;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        
        /* Tour Dates Table */
        .tour-table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        .tour-row {{
            border-bottom: 1px solid rgba(255,255,255,0.06);
            transition: all 0.2s ease;
            cursor: pointer;
        }}
        
        .tour-row:hover {{
            background: rgba(255,255,255,0.03);
            border-color: var(--accent-color);
        }}
        
        .tour-cell {{
            padding: 18px 12px;
            font-size: 0.95rem;
        }}
        
        .cell-date {{
            font-weight: 600;
            color: var(--accent-color);
            width: 90px;
        }}
        
        .cell-venue {{
            color: #fff;
            font-weight: 500;
        }}
        
        .cell-location {{
            color: var(--text-secondary);
        }}
        
        .btn-ticket {{
            display: inline-block;
            background: var(--accent-color);
            color: #fff;
            padding: 6px 14px;
            border-radius: 6px;
            text-decoration: none;
            font-size: 0.85rem;
            font-weight: 600;
            transition: all 0.2s ease;
            text-align: center;
        }}
        
        .btn-ticket:hover {{
            transform: translateY(-2px);
            box-shadow: 0 0 15px var(--accent-color);
        }}
        
        /* Media & EPK styling */
        .bio-selectors {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }}
        
        .bio-btn {{
            background: rgba(255,255,255,0.05);
            border: 1px solid var(--glass-border);
            color: var(--text-secondary);
            padding: 8px 16px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 500;
            font-size: 0.85rem;
            transition: all 0.2s ease;
        }}
        
        .bio-btn.active, .bio-btn:hover {{
            background: var(--accent-color);
            color: #fff;
            border-color: var(--accent-color);
        }}
        
        .bio-content {{
            font-size: 1.05rem;
            color: var(--text-secondary);
            min-height: 120px;
        }}
        
        /* Audio Player Embed */
        .player-wrapper {{
            margin-top: 30px;
            border-radius: 12px;
            overflow: hidden;
            background: #000;
            line-height: 0;
        }}
        
        .player-wrapper iframe {{
            border: none;
            width: 100%;
            height: 80px;
        }}
        
        /* Promoter Package Downloads */
        .rider-list {{
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 15px;
            margin-top: 20px;
        }}
        
        .rider-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(255,255,255,0.02);
            padding: 15px 20px;
            border: 1px solid var(--glass-border);
            border-radius: 10px;
            transition: all 0.2s ease;
        }}
        
        .rider-item:hover {{
            background: rgba(255,255,255,0.05);
            transform: translateX(4px);
        }}
        
        .rider-name {{
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .btn-download {{
            background: rgba(255,255,255,0.08);
            border: none;
            color: #fff;
            padding: 6px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.8rem;
            font-weight: 500;
            transition: all 0.2s ease;
            text-decoration: none;
        }}
        
        .btn-download:hover {{
            background: var(--accent-color);
        }}
        
        footer {{
            text-align: center;
            padding: 40px;
            border-top: 1px solid var(--glass-border);
            color: var(--text-muted);
            font-size: 0.85rem;
        }}
    </style>
</head>
<body>

    <header class="glass-header">
        <a href="#" class="brand-logo">LX8<span>.</span>EVENTS</a>
        <ul class="nav-links">
            <li><a href="#tour">Tour Dates</a></li>
            <li><a href="#about">EPK Press Kit</a></li>
            <li><a href="#booking">Promoter Hub</a></li>
        </ul>
    </header>

    <div class="container">
        
        <!-- HERO AREA -->
        <section class="hero">
            <div class="hero-text">
                <div class="hero-subtitle">{art.get("sub")}</div>
                <h1 class="hero-title">{art.get("name")}</h1>
                <p class="hero-bio">{art.get("bio")}</p>
                
                <div class="pulse-card glass-card" style="padding: 20px; margin-top: 30px; display: inline-flex; align-items: center; gap: 15px; border-radius: 12px;">
                    <div style="width: 10px; height: 10px; border-radius: 50%; background: var(--accent-color); box-shadow: 0 0 10px var(--accent-color);"></div>
                    <span style="font-weight: 600; font-size: 0.85rem; letter-spacing: 1px; text-transform: uppercase;">BEAT SYNC PULSE ACTIVE ({bpm} BPM)</span>
                </div>
            </div>
            
            <div class="hero-visuals">
                <div class="globe-container">
                    <canvas id="tour-globe"></canvas>
                    <div class="globe-tooltip" id="globe-tip">London</div>
                </div>
            </div>
        </section>

        <!-- TOUR DATES -->
        <section id="tour" class="glass-card" style="margin-bottom: 80px;">
            <h2 class="section-title"><span>✈️</span> Live Tour Route</h2>
            
            <table class="tour-table">
                <thead>
                    <tr style="border-bottom: 2px solid rgba(255,255,255,0.08); text-align: left;">
                        <th class="tour-cell" style="color: var(--text-secondary); font-weight: 600;">Date</th>
                        <th class="tour-cell" style="color: var(--text-secondary); font-weight: 600;">Venue</th>
                        <th class="tour-cell" style="color: var(--text-secondary); font-weight: 600;">Location</th>
                        <th class="tour-cell" style="color: var(--text-secondary); font-weight: 600; text-align: right;">Tickets</th>
                    </tr>
                </thead>
                <tbody id="tour-dates-body">
                    <!-- Dates will load dynamically or fall back -->
                </tbody>
            </table>
        </section>

        <div class="grid-2">
            
            <!-- EPK BIO SECTION -->
            <section id="about" class="glass-card">
                <h2 class="section-title"><span>📰</span> Electronic Press Kit</h2>
                <div class="bio-selectors">
                    <button class="bio-btn active" onclick="setBio('short')">Short Pitch</button>
                    <button class="bio-btn" onclick="setBio('long')">Long Bio</button>
                </div>
                <p class="bio-content" id="bio-display-box">Loading bio formats...</p>
                
                <h3 style="font-family: var(--font-brand); margin-top: 30px; margin-bottom: 15px; font-size: 1.1rem; color: #fff;">Featured Music Release</h3>
                <div class="player-wrapper">
                    <iframe src="{art.get("spotify_embed")}" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>
                </div>
            </section>

            <!-- PROMOTER B2B DIRECT DOWNLOADS -->
            <section id="booking" class="glass-card">
                <h2 class="section-title"><span>⚙️</span> Promoter Booking Kit</h2>
                <p style="color: var(--text-secondary); margin-bottom: 25px;">Verified local night promoters can download official stage design requirements and digital branding files directly.</p>
                
                <ul class="rider-list">
                    <li class="rider-item">
                        <div class="rider-name">📄 Technical Stage Rider</div>
                        <a href="#" class="btn-download" onclick="alert('Downloading stage specifications...'); return false;">PDF</a>
                    </li>
                    <li class="rider-item">
                        <div class="rider-name">📄 Hospitality Rider</div>
                        <a href="#" class="btn-download" onclick="alert('Downloading hospitality schedule...'); return false;">PDF</a>
                    </li>
                    <li class="rider-item">
                        <div class="rider-name">🎨 Press Logos Bundle</div>
                        <a href="#" class="btn-download" onclick="alert('Downloading logo asset pack...'); return false;">ZIP (PNG/SVG)</a>
                    </li>
                    <li class="rider-item">
                        <div class="rider-name">📸 High-Res Press Photos</div>
                        <a href="#" class="btn-download" onclick="alert('Downloading official photo package...'); return false;">ZIP (JPEG)</a>
                    </li>
                </ul>
                
                <div style="margin-top: 35px; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 20px;">
                    <div style="font-size: 0.85rem; color: var(--text-muted); text-transform: uppercase; font-weight: 600; letter-spacing: 1px;">Booking Enquiries</div>
                    <div style="font-size: 1.05rem; font-weight: 500; margin-top: 4px; color: #fff;">booking@lx8.events</div>
                </div>
            </section>

        </div>

    </div>

    <footer>
        <p>© 2026 LX8 Events & Management. All rights reserved.</p>
    </footer>

    <!-- INTERACTIVE 3D PARTICLES CANVAS GLOBE ENGINE -->
    <script>
        const tourDates = {dates_json};
        const artistBioShort = "{art.get("bio")}";
        const artistBioLong = "{art.get("bio")} world-renowned electronic architect, delivering state-of-the-art live audio sets global venues. Backed by key underground catalogs, performing modular sets.";

        // Load Bio function
        function setBio(type) {{
            const btns = document.querySelectorAll('.bio-btn');
            btns.forEach(btn => btn.classList.remove('active'));
            
            if (type === 'short') {{
                document.getElementById('bio-display-box').innerText = artistBioShort;
                event.currentTarget.classList.add('active');
            }} else {{
                document.getElementById('bio-display-box').innerText = artistBioLong;
                event.currentTarget.classList.add('active');
            }}
        }}
        
        // Populate Table
        function renderDatesTable() {{
            const tbody = document.getElementById('tour-dates-body');
            tbody.innerHTML = '';
            
            if (tourDates.length === 0) {{
                tbody.innerHTML = `<tr><td colspan="4" class="tour-cell" style="text-align: center; color: var(--text-secondary);">No active tour dates. Routing windows open.</td></tr>`;
                return;
            }}
            
            tourDates.forEach((ev, idx) => {{
                const tr = document.createElement('tr');
                tr.className = 'tour-row';
                tr.onclick = () => {{
                    // Hover/Highlight on the globe
                    focusGlobeOnCity(ev.lat, ev.lng, ev.city);
                }};
                
                tr.innerHTML = `
                    <td class="tour-cell cell-date">${{ev.date}}</td>
                    <td class="tour-cell cell-venue">${{ev.venue}}</td>
                    <td class="tour-cell cell-location">${{ev.city}}, ${{ev.country}}</td>
                    <td class="tour-cell" style="text-align: right;">
                        <a href="#" class="btn-ticket" onclick="alert('Redirecting to secure tickets system for ' + '${{ev.city}}' + '...'); return false;">Tickets</a>
                    </td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        // Canvas Globe Renderer
        const canvas = document.getElementById('tour-globe');
        const ctx = canvas.getContext('2d');
        let width = 360, height = 360;
        
        // High DPI Support
        const dpr = window.devicePixelRatio || 1;
        canvas.width = width * dpr;
        canvas.height = height * dpr;
        ctx.scale(dpr, dpr);
        
        let rotationX = 0.4;
        let rotationY = 0.0;
        let scale = 120; // sphere radius
        let isDragging = false;
        let prevMouseX = 0, prevMouseY = 0;
        let points = [];
        
        // Build 3D sphere grid
        for (let phi = 0.1; phi < Math.PI; phi += 0.2) {{
            for (let theta = 0; theta < 2 * Math.PI; theta += 0.2) {{
                let x = Math.sin(phi) * Math.cos(theta);
                let y = Math.cos(phi);
                let z = Math.sin(phi) * Math.sin(theta);
                points.push({{x, y, z}});
            }}
        }}
        
        // Lat/Lng projection utility
        function projectLatLng(lat, lng) {{
            const phi = (90 - lat) * (Math.PI / 180);
            const theta = (lng + 180) * (Math.PI / 180);
            return {{
                x: -(Math.sin(phi) * Math.sin(theta)),
                y: Math.cos(phi),
                z: Math.sin(phi) * Math.cos(theta)
            }};
        }}
        
        let focusedCity = null;
        let focusTimer = 0;
        let targetRotX = 0.4, targetRotY = 0;
        
        function focusGlobeOnCity(lat, lng, cityName) {{
            const proj = projectLatLng(lat, lng);
            // Compute target rotations to place this coordinate front and center
            targetRotY = -Math.atan2(proj.x, proj.z);
            targetRotX = Math.asin(proj.y);
            
            focusTimer = 40; // run interpolation
            
            const tooltip = document.getElementById('globe-tip');
            tooltip.innerText = cityName;
            tooltip.style.left = '50%';
            tooltip.style.top = '40%';
            tooltip.style.transform = 'translate(-50%, -50%)';
            tooltip.style.display = 'block';
            
            setTimeout(() => {{ tooltip.style.display = 'none'; }}, 2000);
        }}
        
        // Rotate point in 3D
        function rotate3D(pt, rotX, rotY) {{
            // Rotate Y-axis
            let cosY = Math.cos(rotY), sinY = Math.sin(rotY);
            let x1 = pt.x * cosY - pt.z * sinY;
            let z1 = pt.x * sinY + pt.z * cosY;
            
            // Rotate X-axis
            let cosX = Math.cos(rotX), sinX = Math.sin(rotX);
            let y2 = pt.y * cosX - z1 * sinX;
            let z2 = pt.y * sinX + z1 * cosX;
            
            return {{x: x1, y: y2, z: z2}};
        }}
        
        function drawGlobe() {{
            ctx.clearRect(0, 0, width, height);
            
            // Background grid shadow glow
            ctx.fillStyle = 'rgba(18, 16, 28, 0.4)';
            ctx.beginPath();
            ctx.arc(width/2, height/2, scale, 0, 2*Math.PI);
            ctx.fill();
            
            // 1. Draw Globe Wireframe Particles
            points.forEach(pt => {{
                const rPt = rotate3D(pt, rotationX, rotationY);
                if (rPt.z > -0.2) {{ // skip back side details
                    const px = width/2 + rPt.x * scale;
                    const py = height/2 - rPt.y * scale;
                    
                    const depth = (rPt.z + 1.0) / 2.0;
                    ctx.fillStyle = `rgba(255, 255, 255, ${{0.03 + depth * 0.15}})`;
                    ctx.beginPath();
                    ctx.arc(px, py, 1.2, 0, 2*Math.PI);
                    ctx.fill();
                }}
            }});
            
            // 2. Draw Tour Active Coordinates
            tourDates.forEach(ev => {{
                const p = projectLatLng(ev.lat, ev.lng);
                const rp = rotate3D(p, rotationX, rotationY);
                
                if (rp.z > 0.0) {{ // Render active dots in front hemisphere
                    const px = width/2 + rp.x * scale;
                    const py = height/2 - rp.y * scale;
                    
                    // Ripple pulsation effect
                    const glowScale = 1.0 + 0.3 * Math.sin(Date.now() / 200);
                    
                    // Draw outer glowing aura
                    ctx.fillStyle = 'rgba({accent_color.replace("#", "")}, 0.2)';
                    ctx.beginPath();
                    ctx.arc(px, py, 8 * glowScale, 0, 2*Math.PI);
                    ctx.fill();
                    
                    // Draw core glowing dot
                    ctx.fillStyle = 'var(--accent-color)';
                    ctx.beginPath();
                    ctx.arc(px, py, 4, 0, 2*Math.PI);
                    ctx.fill();
                }}
            }});
        }}
        
        function animate() {{
            if (focusTimer > 0) {{
                // Interpolate rotations smoothly
                rotationX += (targetRotX - rotationX) * 0.15;
                rotationY += (targetRotY - rotationY) * 0.15;
                focusTimer--;
            }} else if (!isDragging) {{
                // Gentle ambient rotation
                rotationY += 0.003;
            }}
            
            drawGlobe();
            requestAnimationFrame(animate);
        }}
        
        // Mouse dragging controls
        canvas.addEventListener('mousedown', (e) => {{
            isDragging = true;
            prevMouseX = e.clientX;
            prevMouseY = e.clientY;
        }});
        
        window.addEventListener('mouseup', () => isDragging = false);
        
        canvas.addEventListener('mousemove', (e) => {{
            if (isDragging) {{
                const deltaX = e.clientX - prevMouseX;
                const deltaY = e.clientY - prevMouseY;
                
                rotationY += deltaX * 0.007;
                rotationX -= deltaY * 0.007;
                
                // Limit X rotations to prevent flipping over
                rotationX = Math.max(-Math.PI/2.5, Math.min(Math.PI/2.5, rotationX));
                
                prevMouseX = e.clientX;
                prevMouseY = e.clientY;
            }}
        }});
        
        // Initialize
        document.addEventListener('DOMContentLoaded', () => {{
            setBio('short');
            renderDatesTable();
            animate();
        }});
    </script>
</body>
</html>
"""
    return html

# -------------------------------------------------------------
# HIGH-FIDELITY VENUE-SPECIFIC PROMOTER LANDING PAGE HTML COMPILER
# -------------------------------------------------------------
def build_promoter_portal(artist_id, event_index):
    artist = get_artist_metadata(artist_id)
    dates = artist.get("dates", [])
    
    if event_index < 0 or event_index >= len(dates):
        # Fallback to general bookings
        event_info = {"date": "TBA", "venue": "Main Arena", "city": "Worldwide", "country": "GLOBE"}
    else:
        event_info = dates[event_index]
        
    name = artist.get("name")
    avatar_class = artist.get("avatarClass", "gui")
    
    # localized promotion header
    local_slug = f"{name.upper()} LIVE IN {event_info['city'].upper()}"
    accent = "#ff007f" if avatar_class == "duker" else "#00f3ff"
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Promoter Deck | {name} @ {event_info['venue']}</title>
    
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@600;800&family=Syne:wght@800&display=swap" rel="stylesheet">
    
    <style>
        :root {{
            --bg-base: #07060b;
            --accent: {accent};
            --glass-bg: rgba(18, 14, 28, 0.6);
            --glass-border: rgba(255, 255, 255, 0.08);
            --text-primary: #f3f3f7;
            --text-secondary: #a09eb5;
            --font-ui: 'Inter', sans-serif;
            --font-brand: 'Outfit', sans-serif;
        }}
        
        body {{
            font-family: var(--font-ui);
            background-color: var(--bg-base);
            background-image: radial-gradient(circle at 10% 20%, rgba(15, 8, 30, 0.95) 0%, rgba(4, 9, 20, 0.95) 100%);
            color: var(--text-primary);
            padding: 40px 20px;
            min-height: 100vh;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}
        
        .glass-card {{
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 20px;
            padding: 40px;
            backdrop-filter: blur(20px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            margin-bottom: 30px;
        }}
        
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--glass-border);
            padding-bottom: 25px;
            margin-bottom: 35px;
        }}
        
        .logo {{
            font-family: var(--font-brand);
            font-weight: 800;
            font-size: 1.3rem;
            letter-spacing: 2px;
        }}
        
        .logo span {{
            color: var(--accent);
        }}
        
        .portal-title {{
            font-family: var(--font-brand);
            font-weight: 800;
            font-size: 2.2rem;
            line-height: 1.2;
            margin-bottom: 8px;
        }}
        
        .subtitle {{
            color: var(--accent);
            text-transform: uppercase;
            font-weight: 600;
            letter-spacing: 2px;
            font-size: 0.9rem;
            margin-bottom: 20px;
        }}
        
        .event-badge {{
            display: inline-flex;
            background: rgba(255,255,255,0.04);
            border: 1px solid var(--glass-border);
            padding: 10px 20px;
            border-radius: 12px;
            gap: 20px;
            font-weight: 500;
            font-size: 0.95rem;
            margin-bottom: 30px;
        }}
        
        .badge-val {{
            color: #fff;
            font-weight: 600;
        }}
        
        .grid-2 {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }}
        
        @media(max-width: 750px) {{
            .grid-2 {{
                grid-template-columns: 1fr;
            }}
        }}
        
        /* Interactive local simulator overlay */
        .simulator-box {{
            width: 100%;
            height: 480px;
            background: #000;
            border-radius: 14px;
            overflow: hidden;
            border: 1px solid var(--glass-border);
            position: relative;
            box-shadow: 0 8px 25px rgba(0,0,0,0.5);
        }}
        
        .sim-video-bg {{
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: radial-gradient(circle, rgba(30,12,50,1) 0%, rgba(5,6,15,1) 100%);
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        
        .sim-circle-pulsate {{
            width: 140px; height: 140px;
            border-radius: 50%;
            border: 2px solid var(--accent);
            opacity: 0.15;
            animation: pulseWave 2s infinite ease-out;
        }}
        
        @keyframes pulseWave {{
            0% {{ transform: scale(0.6); opacity: 0.8; }}
            100% {{ transform: scale(1.8); opacity: 0; }}
        }}
        
        .sim-overlay-content {{
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            align-items: center;
            padding: 40px 20px;
            z-index: 2;
            text-align: center;
        }}
        
        .overlay-logo {{
            font-family: var(--font-brand);
            font-weight: 800;
            font-size: 2.2rem;
            color: #fff;
            letter-spacing: 2px;
            text-shadow: 0 0 15px var(--accent);
        }}
        
        .overlay-center-cta {{
            background: rgba(255,255,255,0.08);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.15);
            padding: 15px 30px;
            border-radius: 12px;
            font-weight: 700;
            font-size: 1.1rem;
            color: #fff;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            text-shadow: 0 0 5px rgba(255,255,255,0.5);
            letter-spacing: 1px;
        }}
        
        .overlay-footer-cta {{
            font-weight: 600;
            font-size: 0.9rem;
            letter-spacing: 1.5px;
            color: var(--accent);
            text-transform: uppercase;
        }}
        
        /* Form inputs & buttons */
        .btn {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background: var(--accent);
            color: #fff;
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            width: 100%;
            margin-top: 15px;
        }}
        
        .btn:hover {{
            box-shadow: 0 0 20px var(--accent);
            transform: translateY(-2px);
        }}
        
        /* Promoter Readiness Checklist */
        .chk-row {{
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 12px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }}
        
        .chk-box {{
            width: 20px;
            height: 20px;
            border-radius: 4px;
            border: 2px solid var(--accent);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 0.75rem;
            transition: all 0.2s ease;
        }}
        
        .chk-box.active {{
            background: var(--accent);
            color: #fff;
        }}
        
        .chk-label {{
            color: var(--text-secondary);
            font-size: 0.95rem;
        }}
    </style>
</head>
<body>

    <div class="container">
        
        <div class="glass-card">
            <div class="header">
                <div class="logo">LX8<span>.</span>PROMOTER</div>
                <div style="font-size: 0.8rem; background: rgba(255,255,255,0.05); padding: 4px 10px; border-radius: 4px; border: 1px solid var(--glass-border);">PORTAL GENERATED</div>
            </div>
            
            <div class="subtitle">Official Local Promoter Pack</div>
            <h1 class="portal-title">{local_slug}</h1>
            
            <div class="event-badge">
                <div>Date: <span class="badge-val">{event_info['date']}</span></div>
                <div>Venue: <span class="badge-val">{event_info['venue']}</span></div>
                <div>City: <span class="badge-val">{event_info['city']}</span></div>
            </div>
            
            <p style="color: var(--text-secondary); margin-bottom: 30px;">Welcome to your localized visual briefing. This portal has been pre-configured to output show-ready visual overlay files containing your venue branding. Double check local stage inputs and download your deliverables below.</p>
        </div>

        <div class="grid-2">
            
            <!-- visual card preview -->
            <div class="glass-card" style="padding: 25px;">
                <h3 style="font-family: var(--font-brand); margin-bottom: 15px;">Automated Video Flyer Overlay</h3>
                <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 20px;">This 9:16 mobile promotional video includes high-fidelity overlays customized with your local show date.</p>
                
                <div class="simulator-box">
                    <div class="sim-video-bg">
                        <div class="sim-circle-pulsate"></div>
                    </div>
                    
                    <div class="sim-overlay-content">
                        <div class="overlay-logo">{name.upper()}</div>
                        <div class="overlay-center-cta">{event_info['venue'].upper()}</div>
                        <div class="overlay-footer-cta">{event_info['date']} - LISBON IN BIO</div>
                    </div>
                </div>
                
                <a href="#" class="btn" onclick="alert('Preparing personalized high-quality MP4 file for download...'); return false;">Download Localized Video (.MP4)</a>
            </div>

            <!-- venue readiness checklist & assets -->
            <div class="glass-card" style="display: flex; flex-direction: column; justify-content: space-between;">
                <div>
                    <h3 style="font-family: var(--font-brand); margin-bottom: 15px;">Venue Readiness Checklist</h3>
                    <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 20px;">Please check that your venue technical team has arranged the required audio routing and monitoring specifications.</p>
                    
                    <div class="chk-row">
                        <div class="chk-box active" onclick="this.classList.toggle('active')">✓</div>
                        <div class="chk-label">Pioneer DJM-V10 / 900NXS2 mixer arranged</div>
                    </div>
                    <div class="chk-row">
                        <div class="chk-box active" onclick="this.classList.toggle('active')">✓</div>
                        <div class="chk-label">2x Pioneer CDJ-3000s in Link mode</div>
                    </div>
                    <div class="chk-row">
                        <div class="chk-box" onclick="this.classList.toggle('active')">✓</div>
                        <div class="chk-label">Dual stereo booth monitors (independent volume)</div>
                    </div>
                    <div class="chk-row">
                        <div class="chk-box" onclick="this.classList.toggle('active')">✓</div>
                        <div class="chk-label">Clean stereo electrical connection (unbalanced XLR)</div>
                    </div>
                </div>
                
                <div style="margin-top: 30px;">
                    <h3 style="font-family: var(--font-brand); margin-bottom: 15px; font-size: 1.05rem;">Technical & Press Deliverables</h3>
                    <div style="display: flex; flex-direction: column; gap: 10px;">
                        <a href="#" class="btn" style="background: rgba(255,255,255,0.06); border: 1px solid var(--glass-border); margin: 0;" onclick="alert('Downloading stage specification rider...'); return false;">📄 Download Technical Rider (PDF)</a>
                        <a href="#" class="btn" style="background: rgba(255,255,255,0.06); border: 1px solid var(--glass-border); margin: 0;" onclick="alert('Downloading brand graphics bundle...'); return false;">🎨 Download Brand Assets (.ZIP)</a>
                    </div>
                </div>
            </div>

        </div>

    </div>

</body>
</html>
"""
    return html

# -------------------------------------------------------------
# DUAL SSE LOG VIEW STREAMER / REST INTERRUPT SERVER HANDLING
# -------------------------------------------------------------
class LX8EventsHandler(BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path == "/" or path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open(os.path.join(WORKSPACE_DIR, "index.html"), "rb") as f:
                self.wfile.write(f.read())
            return

        elif path == "/api/artists":
            artists_dir = os.path.join(WORKSPACE_DIR, "artists")
            artists = {}
            if os.path.exists(artists_dir):
                for folder in os.listdir(artists_dir):
                    folder_path = os.path.join(artists_dir, folder)
                    if os.path.isdir(folder_path) and not folder.startswith("."):
                        artists[folder] = get_artist_metadata(folder)
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(artists).encode("utf-8"))
            return

        # DYNAMIC LIVE PROFILE ENGINE
        elif path.startswith("/artists/") and path.endswith("/web"):
            parts = path.split("/")
            artist_id = parts[2]
            
            artist_path = os.path.join(WORKSPACE_DIR, "artists", artist_id)
            if not os.path.exists(artist_path):
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Artist Not Found")
                return

            metadata = get_artist_metadata(artist_id)
            html = build_html_template(metadata)
            
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
            return

        # DYNAMIC LOCALIZED PROMOTER PORTAL ENGINE
        elif path.startswith("/promoter/"):
            artist_id = path.split("/")[-1]
            query = urllib.parse.parse_qs(parsed_url.query)
            event_idx = int(query.get("event", [0])[0])
            
            artist_path = os.path.join(WORKSPACE_DIR, "artists", artist_id)
            if not os.path.exists(artist_path):
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Artist Not Found")
                return

            html = build_promoter_portal(artist_id, event_idx)
            
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
            return

        elif path.startswith("/api/stream/"):
            action = path.split("/")[-1]
            query = urllib.parse.parse_qs(parsed_url.query)
            artist_id = query.get("artist", ["gui-boratto"])[0]
            
            artist_path = os.path.join(WORKSPACE_DIR, "artists", artist_id)
            if not os.path.exists(artist_path):
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Artist not found")
                return

            cmd = []
            cwd = artist_path
            
            if action == "compile":
                cmd = ["swiftc", "-O", "src/video_editor.swift", "-o", "src/video_editor"]
            elif action == "render":
                cmd = ["python3", "scripts/render_all_videos.py"]
            elif action == "sync":
                cmd = ["python3", "scripts/sync_to_gdrive.py"]
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Invalid stream action")
                return

            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.end_headers()

            try:
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    cwd=cwd
                )
                
                if proc.stdout:
                    for line in proc.stdout:
                        sse_line = f"data: {line.rstrip()}\n\n"
                        self.wfile.write(sse_line.encode("utf-8"))
                        self.wfile.flush()
                
                proc.wait()
                exit_code = proc.returncode
                self.wfile.write(f"data: [PROCESS_COMPLETED] {exit_code}\n\n".encode("utf-8"))
                self.wfile.flush()
            except Exception as e:
                self.wfile.write(f"data: [ERROR] Failed to execute process: {str(e)}\n\n".encode("utf-8"))
                self.wfile.flush()
            return

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
            return

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')

        if path.startswith("/api/artists/") and path.endswith("/dates"):
            parts = path.split("/")
            artist_id = parts[3]
            artist_path = os.path.join(WORKSPACE_DIR, "artists", artist_id)
            
            if not os.path.exists(artist_path):
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Artist not found")
                return

            try:
                payload = json.loads(post_data)
                csv_path = os.path.join(artist_path, "tour_dates.csv")
                
                with open(csv_path, "w", encoding="utf-8") as f:
                    f.write("# Tour dates updated dynamically\n")
                    f.write("# Fields: Date, Venue, City, Country_Code\n")
                    for row in payload:
                        date = row.get("date", "").strip()
                        venue = row.get("venue", "").strip()
                        city = row.get("city", "").strip()
                        country = row.get("country", "").strip()
                        if date and venue and city:
                            f.write(f"{date},{venue},{city},{country}\n")

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": True}).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode("utf-8"))
            return

        elif path.startswith("/api/artists/") and path.endswith("/metadata"):
            parts = path.split("/")
            artist_id = parts[3]
            artist_path = os.path.join(WORKSPACE_DIR, "artists", artist_id)
            
            if not os.path.exists(artist_path):
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Artist not found")
                return

            try:
                payload = json.loads(post_data)
                metadata_path = os.path.join(artist_path, "artist.json")
                
                old_metadata = get_artist_metadata(artist_id)
                # Remove dates key from merge
                if "dates" in old_metadata:
                    del old_metadata["dates"]
                
                for k, v in payload.items():
                    old_metadata[k] = v
                old_metadata["id"] = artist_id
                
                with open(metadata_path, "w", encoding="utf-8") as f:
                    json.dump(old_metadata, f, indent=2)

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "metadata": old_metadata}).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode("utf-8"))
            return

        # NEW STATIC SITE COMPILATION TRIGGER
        elif path.startswith("/api/artists/") and path.endswith("/build-web"):
            parts = path.split("/")
            artist_id = parts[3]
            artist_path = os.path.join(WORKSPACE_DIR, "artists", artist_id)
            
            if not os.path.exists(artist_path):
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Artist not found")
                return

            try:
                payload = json.loads(post_data)
                
                # First update metadata
                metadata_path = os.path.join(artist_path, "artist.json")
                metadata = get_artist_metadata(artist_id)
                if "dates" in metadata:
                    del metadata["dates"]
                
                for k, v in payload.items():
                    metadata[k] = v
                
                with open(metadata_path, "w", encoding="utf-8") as f:
                    json.dump(metadata, f, indent=2)

                # Re-fetch populated metadata with dates
                full_metadata = get_artist_metadata(artist_id)
                
                # Render template string
                compiled_html = build_html_template(full_metadata)
                
                # Write to Final_Deliverables/web/index.html
                web_dir = os.path.join(artist_path, "Final_Deliverables", "web")
                os.makedirs(web_dir, exist_ok=True)
                index_path = os.path.join(web_dir, "index.html")
                
                with open(index_path, "w", encoding="utf-8") as f:
                    f.write(compiled_html)

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": True, 
                    "path": index_path,
                    "url": f"/artists/{artist_id}/web"
                }).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode("utf-8"))
            return

        elif path == "/api/artists":
            try:
                payload = json.loads(post_data)
                name = payload.get("name", "").strip()
                sub = payload.get("sub", "").strip() or "Electronic Producer"
                bio = payload.get("bio", "").strip() or "Curated artist for LX8 Events."
                
                if not name:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b"Artist Name is required")
                    return

                artist_id = name.lower().replace(" ", "-").replace("/", "-")
                artist_path = os.path.join(WORKSPACE_DIR, "artists", artist_id)
                
                if os.path.exists(artist_path):
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b"Artist already exists")
                    return

                os.makedirs(artist_path, exist_ok=True)
                source_artist = os.path.join(WORKSPACE_DIR, "artists", "gui-boratto")
                
                # Copy standard scripts and structures
                shutil.copytree(os.path.join(source_artist, "src"), os.path.join(artist_path, "src"))
                shutil.copytree(os.path.join(source_artist, "scripts"), os.path.join(artist_path, "scripts"))
                os.makedirs(os.path.join(artist_path, "Final_Deliverables"), exist_ok=True)
                os.makedirs(os.path.join(artist_path, "Sources_and_Assets"), exist_ok=True)
                
                # Copy assets securely
                source_assets = os.path.join(source_artist, "Sources_and_Assets")
                dest_assets = os.path.join(artist_path, "Sources_and_Assets")
                for item in os.listdir(source_assets):
                    s_file = os.path.join(source_assets, item)
                    d_file = os.path.join(dest_assets, item)
                    if os.path.isfile(s_file) and os.path.getsize(s_file) < 2 * 1024 * 1024:
                        shutil.copy2(s_file, d_file)
                
                csv_path = os.path.join(artist_path, "tour_dates.csv")
                with open(csv_path, "w", encoding="utf-8") as f:
                    f.write("# Tour dates updated dynamically\n")
                    f.write("# Fields: Date, Venue, City, Country_Code\n")
                    f.write("10 Sep,Mainstage,Lisbon,PT\n")

                metadata = {
                    "id": artist_id,
                    "name": name,
                    "sub": sub,
                    "bio": bio,
                    "avatar": "".join([w[0] for w in name.split() if w])[:2].upper(),
                    "avatarClass": "gui" if "gui" in artist_id else "duker",
                    "redirect": f"LINK IN BIO - {name.upper().replace(' ', '')}.COM",
                    "web_title": f"{name} | Official Web Portal",
                    "web_description": f"Official tour dates and media kit for {name}.",
                    "spotify_embed": "https://open.spotify.com/embed/track/3b5uT21XJ8J8Fk72412v6Z",
                    "bpm": 124,
                    "web_theme": "glass",
                    "mesh_color": "classic"
                }
                
                metadata_path = os.path.join(artist_path, "artist.json")
                with open(metadata_path, "w", encoding="utf-8") as f:
                    json.dump(metadata, f, indent=2)

                metadata["dates"] = [{"date": "10 Sep", "venue": "Mainstage", "city": "Lisbon", "country": "PT", "lat": 38.7223, "lng": -9.1393}]

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "artist": metadata}).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode("utf-8"))
            return

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
            return

def run_server():
    server_address = ('', PORT)
    httpd = ThreadingTCPServer(server_address, LX8EventsHandler)
    print(f"LX8 Events Management Server started at http://localhost:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.shutdown()

if __name__ == "__main__":
    run_server()
