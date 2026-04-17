from fastapi import FastAPI
from pydantic import BaseModel

from downloader import download_video
from transcriber import transcribe
from analyzer import find_peaks
from clipper import create_clips
from subtitle_generator import generate_srt

app = FastAPI()

class VideoRequest(BaseModel):
    youtube_url: str
    clip_length: int = 30
    num_clips: int = 3

@app.get("/")
def home():
    return {"message": "Video Clipper API Running"}

@app.post("/process")
def process_video(req: VideoRequest):
    print("Downloading...")
    video_path = download_video(req.youtube_url)

    print("Transcribing...")
    segments = transcribe(video_path)
    print(f"Segments: {len(segments)}")

    print("Generating subtitles...")
    generate_srt(segments)

    print("Finding peaks...")
    peaks = find_peaks(segments, video_path)
    print(f"Peaks: {peaks}")

    print("Creating clips...")
    clips = create_clips(video_path, peaks, req.clip_length)

    return {"clips": clips}