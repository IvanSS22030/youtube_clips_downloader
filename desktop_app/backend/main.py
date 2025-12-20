from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import asyncio
from typing import Dict, List, Optional
import threading

import os
try:
    from scripts.any_video_downloader import VideoDownloader
    from scripts.image_scraper import ImageScraper
    from scripts.javascript_scraper import JavascriptScraper
    from scripts.yt_clips_downloader import YTClipsDownloader
    from scripts.video_format_converter import VideoFormatConverter
except ImportError:
    # Fallback for dev mode
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), "scripts"))
    from any_video_downloader import VideoDownloader
    from image_scraper import ImageScraper
    from javascript_scraper import JavascriptScraper
    from yt_clips_downloader import YTClipsDownloader
    from video_format_converter import VideoFormatConverter

app = FastAPI()

# Enable CORS for Electron (localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Utils
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "../../"))
DOWNLOADS_DIR = os.path.join(PROJECT_ROOT, "downloads")

# Ensure subdirectories exist
for subdir in ["videos", "images", "js files", "style files", "clips", "converted"]:
    os.makedirs(os.path.join(DOWNLOADS_DIR, subdir), exist_ok=True)

video_tool = VideoDownloader(output_dir=os.path.join(DOWNLOADS_DIR, "videos"))
image_tool = ImageScraper(output_dir=os.path.join(DOWNLOADS_DIR, "images"))
script_tool = JavascriptScraper(output_dir=os.path.join(DOWNLOADS_DIR, "js files"))
clip_tool = YTClipsDownloader(output_dir=os.path.join(DOWNLOADS_DIR, "clips"))
converter_tool = VideoFormatConverter(output_dir=os.path.join(DOWNLOADS_DIR, "converted"))

# Global Event Loop Reference
loop = None

@app.on_event("startup")
async def startup_event():
    global loop
    loop = asyncio.get_running_loop()
    print(f"Captured Main Event Loop: {loop}")

# --- WebSocket Manager ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# --- Helper for Threaded Execution ---
def run_in_thread(target_func, *args, **kwargs):
    def wrapper():
        # Define a callback that talks to WebSocket via Main Loop
        def thread_callback(data):
            if loop and loop.is_running():
                asyncio.run_coroutine_threadsafe(
                    manager.broadcast(json.dumps({
                        "type": "progress",
                        "data": data
                    })), loop
                )
            else:
                print("Error: Main loop not available for progress update")

        try:
            # Inject progress_callback
            target_func(*args, **kwargs, progress_callback=thread_callback)
            
            # Send done if the function didn't send a final 'completed' event
            # (Most of our scripts do, but safe to ensure)
            
        except Exception as e:
            print(f"Thread Error: {e}")
            thread_callback({"status": "error", "error": str(e)})

    t = threading.Thread(target=wrapper)
    t.start()

# --- Models ---
class AnalyzeUrlRequest(BaseModel):
    url: str

class DownloadVideoRequest(BaseModel):
    video: Dict
    format_idx: int

class ScrapeRequest(BaseModel):
    url: str

class ClipRequest(BaseModel):
    url: str

class ConvertRequest(BaseModel):
    file_path: str
    quality: str = "high"

# --- Endpoints ---

@app.get("/")
def read_root():
    return {"status": "ok", "service": "TurboDL Backend"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/analyze")
def analyze_url(req: AnalyzeUrlRequest):
    print(f"Analyzing: {req.url}")
    try:
        videos = video_tool.get_video_info(req.url)
        if not videos:
            return {"found": False}
        return {"found": True, "videos": videos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/download")
def start_download(req: DownloadVideoRequest):
    run_in_thread(video_tool.download_video, req.video, req.format_idx)
    return {"status": "started", "message": "Video download running in background"}

@app.post("/scrape-images")
def start_scrape_images(req: ScrapeRequest):
    run_in_thread(image_tool.download_images, req.url)
    return {"status": "started", "message": "Image scrape running in background"}

@app.post("/scrape-scripts")
def start_scrape_scripts(req: ScrapeRequest):
    run_in_thread(script_tool.download_javascript, req.url)
    return {"status": "started", "message": "Script scrape running in background"}

@app.post("/download-clip")
def start_clip_download(req: ClipRequest):
    run_in_thread(clip_tool.download_clip, req.url)
    return {"status": "started", "message": "Clip download running in background"}

@app.post("/convert")
def start_conversion(req: ConvertRequest):
    run_in_thread(converter_tool.convert_to_mp4, req.file_path, quality_preset=req.quality)
    return {"status": "started", "message": "Conversion running in background"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
