import os
import subprocess

def seconds_to_hhmmss(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"[{int(hours):02}:{int(minutes):02}:{int(secs):02}]"

def get_duration_in_seconds(filepath):
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', filepath],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        output = result.stdout
        if output is None or output.strip() == "":
            raise ValueError("No output from ffprobe")
        duration = float(output.strip())
        return int(duration)
    except Exception as e:
        return None

def create_timestamp_tracklist(txt_path, output_path="tracklist.txt", log_callback=print):
    if not os.path.exists(txt_path):
        log_callback("❌ File danh sách không tồn tại.")
        return

    with open(txt_path, "r", encoding="utf-8") as f:
        video_paths = [line.strip().strip('"') for line in f if line.strip()]

    tracklist = []
    total_seconds = 0

    for filepath in video_paths:
        timestamp = seconds_to_hhmmss(total_seconds)
        title = os.path.splitext(os.path.basename(filepath))[0]

        if not os.path.exists(filepath):
            tracklist.append(f"{timestamp} {title} (File not found)")
            continue

        duration = get_duration_in_seconds(filepath)
        if duration is None:
            tracklist.append(f"{timestamp} {title} (Lỗi đọc thời lượng)")
            continue

        tracklist.append(f"{timestamp} {title}")
        total_seconds += duration

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(tracklist))

    log_callback(f"✅ Tracklist đã tạo tại: {output_path}")
