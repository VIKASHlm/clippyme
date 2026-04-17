import librosa
import numpy as np

def get_audio_energy(video_path):
    y, sr = librosa.load(video_path, sr=None)

    frame_length = 2048
    hop_length = 512

    energy = np.array([
        sum(abs(y[i:i+frame_length]**2))
        for i in range(0, len(y), hop_length)
    ])

    times = librosa.frames_to_time(
        range(len(energy)),
        sr=sr,
        hop_length=hop_length
    )

    return list(zip(times, energy))