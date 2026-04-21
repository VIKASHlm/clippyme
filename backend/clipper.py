def create_clips(video_path, peaks, clip_length, output_dir="clips"):
    import os
    import ffmpeg

    os.makedirs(output_dir, exist_ok=True)

    clips = []

    for i, peak in enumerate(peaks):
        start = max(0, peak["start"])
        output = os.path.join(output_dir, f"clip_{i}.mp4")

        (
            ffmpeg
            .input(video_path, ss=start, t=clip_length)
            .output(
                output,
                vf="subtitles=subtitles.srt:force_style='Fontsize=42,PrimaryColour=&Hffffff&,OutlineColour=&H000000&,BorderStyle=3,Outline=3,Shadow=2,Alignment=2',scale=1080:1920",
                vcodec="libx264",
                acodec="aac"
            )
            .run(overwrite_output=True)
        )

        clips.append(output)

    return clips