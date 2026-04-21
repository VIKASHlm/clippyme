import os
import shutil
import uuid
from threading import Thread

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

# 🔥 folders
os.makedirs("clips", exist_ok=True)
os.makedirs("uploads", exist_ok=True)

app.mount("/clips", StaticFiles(directory="clips"), name="clips")

# 🔥 job storage (simple memory)
jobs = {}


class VideoRequest(BaseModel):
    youtube_url: str
    clip_length: int = 30
    num_clips: int = 3


@app.get("/")
def home():
    return {"message": "ClippyMe API Running 🚀"}


# 🎬 YOUTUBE FLOW (ASYNC)
@app.post("/process")
def process_video(req: VideoRequest):

    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "processing", "clips": []}

    def worker():
        try:
            video_path = download_video(req.youtube_url)
            run_pipeline(job_id, video_path, req.clip_length)
        except Exception as e:
            print("Download failed:", e)
            jobs[job_id] = {"status": "failed"}

    Thread(target=worker).start()

    return {"status": "processing", "job_id": job_id}


# 📁 UPLOAD FLOW (ASYNC)
@app.post("/upload")
def upload_video(file: UploadFile = File(...)):

    job_id = str(uuid.uuid4())
    file_path = f"uploads/{job_id}_{file.filename}"

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        print("Upload error:", e)
        return {"status": "failed", "message": "Upload failed"}

    jobs[job_id] = {"status": "processing", "clips": []}

    Thread(target=run_pipeline, args=(job_id, file_path, 30)).start()

    return {"status": "processing", "job_id": job_id}


# 🔍 STATUS API
@app.get("/status/{job_id}")
def get_status(job_id: str):
    return jobs.get(job_id, {"status": "not_found"})


# 🧠 PIPELINE
def run_pipeline(job_id, video_path, clip_length):
    try:
        segments = transcribe(video_path)
        generate_srt(segments)
        peaks = find_peaks(segments, video_path)
        clips = create_clips(video_path, peaks, clip_length)

        jobs[job_id] = {
            "status": "done",
            "clips": [f"/clips/{c.split('/')[-1]}" for c in clips]
        }

    except Exception as e:
        print("Processing error:", e)
        jobs[job_id] = {"status": "failed"}