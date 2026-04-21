import os
import shutil
import uuid
import json
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

# 🔥 Use /tmp for persistence during runtime
BASE_DIR = "/tmp"
CLIPS_DIR = os.path.join(BASE_DIR, "clips")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

os.makedirs(CLIPS_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/clips", StaticFiles(directory=CLIPS_DIR), name="clips")


# 📦 JOB STORAGE (FILE-BASED in /tmp)

def job_path(job_id):
    return os.path.join(BASE_DIR, f"{job_id}.json")


def save_job(job_id, data):
    with open(job_path(job_id), "w") as f:
        json.dump(data, f)


def load_job(job_id):
    try:
        with open(job_path(job_id), "r") as f:
            return json.load(f)
    except:
        return {"status": "not_found"}


# 📥 REQUEST MODEL
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

    job_id = str(uuid.uuid4())
    save_job(job_id, {"status": "processing", "clips": []})

    def worker():
        try:
            video_path = download_video(req.youtube_url)
            run_pipeline(job_id, video_path, req.clip_length)
        except Exception as e:
            print("Download failed:", e)
            save_job(job_id, {"status": "failed"})

    Thread(target=worker).start()

    return {"status": "processing", "job_id": job_id}


# 📁 UPLOAD FLOW
@app.post("/upload")
def upload_video(file: UploadFile = File(...)):

    job_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{job_id}_{file.filename}")

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        print("Upload error:", e)
        return {"status": "failed", "message": "Upload failed"}

    save_job(job_id, {"status": "processing", "clips": []})

    Thread(target=run_pipeline, args=(job_id, file_path, 30)).start()

    return {"status": "processing", "job_id": job_id}


# 🔍 STATUS API
@app.get("/status/{job_id}")
def get_status(job_id: str):
    return load_job(job_id)


# 🧠 PIPELINE
def run_pipeline(job_id, video_path, clip_length):
    try:
        print("STEP 1: Transcribing...")
        segments = transcribe(video_path)

        print("STEP 2: Generating subtitles...")
        generate_srt(segments)

        print("STEP 3: Finding peaks...")
        peaks = find_peaks(segments, video_path)

        print("STEP 4: Creating clips...")
        clips = create_clips(video_path, peaks, clip_length, CLIPS_DIR)

        print("STEP 5: Done!")

        save_job(job_id, {
            "status": "done",
            "clips": [f"/clips/{os.path.basename(c)}" for c in clips]
        })

    except Exception as e:
        print("Processing error:", e)
        save_job(job_id, {"status": "failed"})