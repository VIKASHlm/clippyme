import yt_dlp
import os

def download_video(url: str, output_path="videos"):
    os.makedirs(output_path, exist_ok=True)

    ydl_opts = {
        'format': 'mp4',
        'outtmpl': f'{output_path}/%(id)s.%(ext)s',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_path = f"{output_path}/{info['id']}.mp4"

    return video_path