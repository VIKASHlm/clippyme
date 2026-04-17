from audio_analyzer import get_audio_energy


# 🔊 Get average energy in segment
def get_energy_score(start, end, energy_data):
    values = [e for t, e in energy_data if start <= t <= end]
    return sum(values) / len(values) if values else 0


# 🧠 Score based on text
def score_segment(text):
    text = text.lower()
    score = 0

    # Engagement signals
    if "?" in text:
        score += 2

    if any(word in text for word in [
        "you", "secret", "truth", "mistake", "never", "always"
    ]):
        score += 2

    # Emotion / hype
    if any(word in text for word in [
        "amazing", "insane", "crazy", "unbelievable", "wow"
    ]):
        score += 3

    # Length (more content = more context)
    score += min(len(text) / 100, 2)

    return score


# 🧩 Merge small segments into bigger chunks (better clips)
def merge_segments(segments, window=15):
    if not segments:
        return []

    merged = []
    current = []
    start_time = segments[0]["start"]

    for seg in segments:
        current.append(seg)

        if seg["end"] - start_time >= window:
            full_text = " ".join(s["text"] for s in current)

            merged.append({
                "start": start_time,
                "end": seg["end"],
                "text": full_text
            })

            current = []
            start_time = seg["end"]

    # Add leftover
    if current:
        full_text = " ".join(s["text"] for s in current)
        merged.append({
            "start": start_time,
            "end": current[-1]["end"],
            "text": full_text
        })

    return merged


# 🎯 Main peak detection
def find_peaks(segments, video_path, top_k=5):
    if not segments:
        return []

    if not isinstance(top_k, int):
        top_k = 5

    energy_data = get_audio_energy(video_path)

    # 🔥 Use merged segments (IMPORTANT)
    merged_segments = merge_segments(segments)

    scored = []

    for seg in merged_segments:
        text_score = score_segment(seg["text"])
        audio_score = get_energy_score(seg["start"], seg["end"], energy_data)

        total_score = text_score + (audio_score * 0.0001)

        scored.append({
            "start": seg["start"],
            "end": seg["end"],
            "score": total_score
        })

    # Sort by best score
    scored.sort(key=lambda x: x["score"], reverse=True)

    return scored[:top_k]