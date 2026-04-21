import os
import shutil
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from downloader import download_video
from transcriber import transcribe
from analyzer import find_peaks
from clipper import create_clips
from subtitle_generator import generate_srt

app = FastAPI()

# 🔥 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 Folders
os.makedirs("clips", exist_ok=True)
os.makedirs("uploads", exist_ok=True)

app.mount("/clips", StaticFiles(directory="clips"), name="clips")

# 🔥 Fix OPTIONS issue
@app.options("/process")
def options_process():
    return {"ok": True}

@app.options("/upload")
def options_upload():
    return {"ok": True}


class VideoRequest(BaseModel):
    youtube_url: str
    clip_length: int = 30
    num_clips: int = 3


@app.get("/")
def home():
    return {"message": "ClippyMe API Running 🚀"}


# 🎬 YOUTUBE FLOW
@app.post("/process")
def process_video(req: VideoRequest):

    try:
        video_path = download_video(req.youtube_url)
    except Exception:
        return {
            "status": "failed",
            "message": "YouTube blocked this video. Try upload instead."
        }

    return process_pipeline(video_path, req.clip_length)


# 📁 UPLOAD FLOW
@app.post("/upload")
def upload_video(file: UploadFile = File(...)):

    try:
        file_path = f"uploads/{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception:
        return {"status": "failed", "message": "Upload failed"}

    return process_pipeline(file_path, 30)


# 🧠 COMMON PIPELINE
def process_pipeline(video_path, clip_length):

    try:
        segments = transcribe(video_path)
        generate_srt(segments)
        peaks = find_peaks(segments, video_path)
        clips = create_clips(video_path, peaks, clip_length)

        return {
            "status": "success",
            "clips": [f"/clips/{clip.split('/')[-1]}" for clip in clips]
        }

    except Exception as e:
        print("Processing error:", str(e))
        return {"status": "failed", "message": "Processing failed"}