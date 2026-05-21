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

class LX8EventsHandler(BaseHTTPRequestHandler):
    def end_headers(self):
        # Allow CORS for easy debugging if necessary
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
            # Serve index.html
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open(os.path.join(WORKSPACE_DIR, "index.html"), "rb") as f:
                self.wfile.write(f.read())
            return

        elif path == "/api/artists":
            # Scan artists directory and return their metadata + dates count
            artists_dir = os.path.join(WORKSPACE_DIR, "artists")
            artists = {}
            if os.path.exists(artists_dir):
                for folder in os.listdir(artists_dir):
                    folder_path = os.path.join(artists_dir, folder)
                    if os.path.isdir(folder_path) and not folder.startswith("."):
                        metadata_path = os.path.join(folder_path, "artist.json")
                        csv_path = os.path.join(folder_path, "tour_dates.csv")
                        
                        # Load or create metadata
                        metadata = {}
                        if os.path.exists(metadata_path):
                            try:
                                with open(metadata_path, "r", encoding="utf-8") as f:
                                    metadata = json.load(f)
                            except Exception:
                                pass
                        
                        if not metadata:
                            name = folder.replace("-", " ").title()
                            metadata = {
                                "id": folder,
                                "name": name,
                                "sub": "Techno / House Producer",
                                "bio": f"Artist {name} curated by LX8 Events.",
                                "avatar": "".join([w[0] for w in name.split() if w])[:2].upper(),
                                "avatarClass": "gui" if "gui" in folder else "duker",
                                "redirect": f"LINK IN BIO - {folder.upper().replace('-', '')}.COM"
                            }
                            # save it
                            with open(metadata_path, "w", encoding="utf-8") as f:
                                json.dump(metadata, f, indent=2)
                        
                        # Count dates
                        dates = []
                        if os.path.exists(csv_path):
                            with open(csv_path, "r", encoding="utf-8") as f:
                                for line in f:
                                    trimmed = line.strip()
                                    if not trimmed or trimmed.startswith("#"):
                                        continue
                                    parts = trimmed.split(",")
                                    if len(parts) >= 4:
                                        dates.append({
                                            "date": parts[0].strip(),
                                            "venue": parts[1].strip(),
                                            "city": parts[2].strip(),
                                            "country": parts[3].strip()
                                        })
                        
                        metadata["dates"] = dates
                        artists[folder] = metadata
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(artists).encode("utf-8"))
            return

        elif path.startswith("/api/stream/"):
            # Stream compilation or render logs via SSE!
            # Path format: /api/stream/compile?artist=<id> or /api/stream/render?artist=<id> or /api/stream/sync?artist=<id>
            # Let's extract command and artist
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
                cmd = ["swiftc", "-O", f"src/video_editor.swift", "-o", f"src/video_editor"]
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

            # Run process and stream stdout/stderr
            try:
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    cwd=cwd
                )
                
                # Stream lines
                if proc.stdout:
                    for line in proc.stdout:
                        # Clean line and format as SSE data
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
        
        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')

        if path.startswith("/api/artists/") and path.endswith("/dates"):
            # Update tour dates for an artist
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
                
                # Write CSV
                with open(csv_path, "w", encoding="utf-8") as f:
                    f.write(f"# Tour dates updated on 2026-05-22\n")
                    f.write(f"# Fields: Date, Venue, City, Country_Code\n")
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
            # Update metadata (artist.json)
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
                
                # Read old metadata to preserve ID and anything else
                old_metadata = {}
                if os.path.exists(metadata_path):
                    with open(metadata_path, "r", encoding="utf-8") as f:
                        old_metadata = json.load(f)
                
                # Merge new values
                for k, v in payload.items():
                    old_metadata[k] = v
                old_metadata["id"] = artist_id  # ensure ID stays consistent
                
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

        elif path == "/api/artists":
            # Create a new artist!
            try:
                payload = json.loads(post_data)
                name = payload.get("name", "").strip()
                sub = payload.get("sub", "").strip() or "Electronic Producer"
                bio = payload.get("bio", "").strip() or "Curated artist for LX8 Events."
                def_style = payload.get("style", "glass")
                
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

                # Create artist directory
                os.makedirs(artist_path, exist_ok=True)
                
                # Copy template structure from gui-boratto (copy code, scripts, but only a basic Sources_and_Assets and empty Final_Deliverables to save space)
                source_artist = os.path.join(WORKSPACE_DIR, "artists", "gui-boratto")
                
                # 1. Copy src
                shutil.copytree(os.path.join(source_artist, "src"), os.path.join(artist_path, "src"))
                # 2. Copy scripts
                shutil.copytree(os.path.join(source_artist, "scripts"), os.path.join(artist_path, "scripts"))
                # 3. Create empty folders
                os.makedirs(os.path.join(artist_path, "Final_Deliverables"), exist_ok=True)
                os.makedirs(os.path.join(artist_path, "Sources_and_Assets"), exist_ok=True)
                
                # 4. Copy logos and images (except large files like video and big JPEG)
                source_assets = os.path.join(source_artist, "Sources_and_Assets")
                dest_assets = os.path.join(artist_path, "Sources_and_Assets")
                for item in os.listdir(source_assets):
                    s_file = os.path.join(source_assets, item)
                    d_file = os.path.join(dest_assets, item)
                    # Skip massive video and massive JPEG (over 2MB)
                    if os.path.isfile(s_file):
                        if os.path.getsize(s_file) < 2 * 1024 * 1024:
                            shutil.copy2(s_file, d_file)
                
                # Symlink the massive video file if it exists, or let it fall back
                s_video = os.path.join(source_assets, "VIDEO-2025-05-08-17-54-08.mp4")
                d_video = os.path.join(dest_assets, "VIDEO-2025-05-08-17-54-08.mp4")
                if os.path.exists(s_video):
                    try:
                        os.symlink(s_video, d_video)
                    except Exception:
                        try:
                            shutil.copy2(s_video, d_video)
                        except Exception:
                            pass

                # 5. Create default tour_dates.csv
                csv_path = os.path.join(artist_path, "tour_dates.csv")
                with open(csv_path, "w", encoding="utf-8") as f:
                    f.write(f"# Tour dates updated on 2026-05-22\n")
                    f.write(f"# Fields: Date, Venue, City, Country_Code\n")
                    f.write(f"10 Sep,Mainstage,Lisbon,PT\n")

                # 6. Save artist.json
                metadata = {
                    "id": artist_id,
                    "name": name,
                    "sub": sub,
                    "bio": bio,
                    "avatar": "".join([w[0] for w in name.split() if w])[:2].upper(),
                    "avatarClass": "gui" if "gui" in artist_id else "duker",
                    "redirect": f"LINK IN BIO - {name.upper().replace(' ', '')}.COM"
                }
                
                metadata_path = os.path.join(artist_path, "artist.json")
                with open(metadata_path, "w", encoding="utf-8") as f:
                    json.dump(metadata, f, indent=2)

                metadata["dates"] = [{
                    "date": "10 Sep",
                    "venue": "Mainstage",
                    "city": "Lisbon",
                    "country": "PT"
                }]

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
    # Using ThreadingTCPServer to handle concurrent request processing (e.g. log streaming)
    httpd = ThreadingTCPServer(server_address, LX8EventsHandler)
    print(f"LX8 Events Management Server started at http://localhost:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.shutdown()

if __name__ == "__main__":
    run_server()
