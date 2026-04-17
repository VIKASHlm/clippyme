import subprocess
import os

def create_clips(video_path, peaks, clip_length=30):
    os.makedirs("clips", exist_ok=True)

    clip_paths = []

    for i, peak in enumerate(peaks):
        start = peak["start"]
        output_file = f"clips/clip_{i}.mp4"

        subtitle_file = "subtitles.srt"
        cmd = [
    "ffmpeg",
    "-y",
    "-i", video_path,
    "-ss", str(start),
    "-t", str(clip_length),
    "-vf", "subtitles=subtitles.srt:force_style='Fontsize=36,PrimaryColour=&Hffffff&,OutlineColour=&H000000&,BorderStyle=3,Alignment=2',scale=1080:1920",
    output_file
]

        subprocess.run(cmd)

        clip_paths.append(output_file)

    return clip_paths