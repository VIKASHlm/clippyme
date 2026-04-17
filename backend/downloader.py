import yt_dlp
import os

def download_video(url: str, output_path="videos"):
    os.makedirs(output_path, exist_ok=True)

    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': f'{output_path}/%(id)s.%(ext)s',

        'noplaylist': True,
        'quiet': False,
        'no_warnings': True,

        # 🔥 Anti-bot fixes
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web']
            }
        },

        'http_headers': {
            'User-Agent': 'Mozilla/5.0'
        },

        # 🔥 Stability improvements
        'socket_timeout': 30,
        'retries': 3,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_path = f"{output_path}/{info['id']}.mp4"
            return video_path

    except Exception as e:
        print("Download error:", str(e))
        raise e