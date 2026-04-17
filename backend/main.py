import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from downloader import download_video
from transcriber import transcribe
from analyzer import find_peaks
from clipper import create_clips
from subtitle_generator import generate_srt

app = FastAPI()

# 🔥 Enable CORS (for React frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
os.makedirs("clips", exist_ok=True)
# 🔥 Serve generated clips
app.mount("/clips", StaticFiles(directory="clips"), name="clips")


class VideoRequest(BaseModel):
    youtube_url: str
    clip_length: int = 30
    num_clips: int = 3


@app.get("/")
def home():
    return {"message": "Video Clipper API Running"}


@app.post("/process")
def process_video(req: VideoRequest):

    # 🔽 DOWNLOAD
    try:
        print("Downloading...")
        video_path = download_video(req.youtube_url)

    except Exception as e:
        print("Download failed:", str(e))
        return {
            "status": "failed",
            "stage": "download",
            "message": "YouTube blocked this video or download failed. Try another video."
        }

    # 🔽 TRANSCRIBE
    try:
        print("Transcribing...")
        segments = transcribe(video_path)
        print(f"Segments: {len(segments)}")

    except Exception as e:
        print("Transcription failed:", str(e))
        return {
            "status": "failed",
            "stage": "transcription",
            "message": "Error during transcription."
        }

    # 🔽 SUBTITLES
    try:
        print("Generating subtitles...")
        generate_srt(segments)

    except Exception as e:
        print("Subtitle generation failed:", str(e))
        return {
            "status": "failed",
            "stage": "subtitles",
            "message": "Error generating subtitles."
        }

    # 🔽 ANALYSIS
    try:
        print("Finding peaks...")
        peaks = find_peaks(segments, video_path)
        print(f"Peaks: {peaks}")

    except Exception as e:
        print("Peak detection failed:", str(e))
        return {
            "status": "failed",
            "stage": "analysis",
            "message": "Error analyzing video."
        }

    # 🔽 CLIPPING
    try:
        print("Creating clips...")
        clips = create_clips(video_path, peaks, req.clip_length)

    except Exception as e:
        print("Clip creation failed:", str(e))
        return {
            "status": "failed",
            "stage": "clipping",
            "message": "Error creating clips."
        }

    # 🔽 SUCCESS RESPONSE
    return {
        "status": "success",
        "clips": [f"/clips/{clip.split('/')[-1]}" for clip in clips]
    }