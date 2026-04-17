from faster_whisper import WhisperModel

model = WhisperModel("base", compute_type="int8")

def transcribe(video_path):
    segments, _ = model.transcribe(video_path)

    result = []
    for seg in segments:
        result.append({
            "start": seg.start,
            "end": seg.end,
            "text": seg.text
        })

    return result