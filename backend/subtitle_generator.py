def generate_srt(segments, output_file="subtitles.srt"):
    with open(output_file, "w", encoding="utf-8") as f:
        index = 1

        for seg in segments:
            words = seg["text"].split()

            chunk_size = 3  # 🔥 controls style (2–4 best)
            duration = seg["end"] - seg["start"]

            if len(words) == 0:
                continue

            time_per_chunk = duration / max(1, len(words) // chunk_size)

            current_time = seg["start"]

            for i in range(0, len(words), chunk_size):
                chunk_words = words[i:i+chunk_size]
                text = " ".join(chunk_words)

                start = format_time(current_time)
                end = format_time(current_time + time_per_chunk)

                f.write(f"{index}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{text}\n\n")

                index += 1
                current_time += time_per_chunk

    return output_file


def format_time(seconds):
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)

    return f"{hrs:02}:{mins:02}:{secs:02},{millis:03}"