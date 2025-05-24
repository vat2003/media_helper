import os
import subprocess
import locale
from PyQt5.QtCore import QThread, pyqtSignal
from utils.tracklist_generator import create_timestamp_tracklist


class FFmpegWorker(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(str)

    def __init__(self, file_path, preset):
        super().__init__()
        self.file_path = file_path
        self.preset = preset

    def run(self):
        start_msg = f"🔄 Starting: {self.preset} → {os.path.basename(self.file_path)}"
        self.progress.emit(start_msg)

        if self.preset == "Generate Tracklist":
            txt_list_path = self.file_path
            output_txt_path = self.file_path.replace(".txt", "_tracklist.txt")
            create_timestamp_tracklist(txt_list_path, output_txt_path, log_callback=self.progress.emit)
            self.finished.emit(f"✅ Tracklist generated: {output_txt_path}")
            return

        output_file = self.file_path.replace(".mp4", f"_{self.preset}.mp4")
        command = ["ffmpeg", "-hide_banner", "-loglevel", "warning", "-y", "-i", self.file_path]

        if self.preset == "Convert to MP4":
            command += ["-c:v", "h264_nvenc", output_file]
        elif self.preset == "Extract Audio":
            output_file = self.file_path.replace(".mp4", ".mp3")
            command += ["-q:a", "0", "-map", "a", output_file]
        elif self.preset == "Resize 720p":
            command += [
                "-vf", "scale=1280:720",
                "-c:v", "h264_nvenc",  # sử dụng NVIDIA GPU encoder
                output_file
            ]
        else:
            output_file = self.file_path.replace(".mp4", "_output.mp4")

        try:
            encoding = locale.getpreferredencoding()
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in process.stdout:
                decoded_line = line.decode(encoding, errors='replace').strip()
                if decoded_line:
                    self.progress.emit(f"{os.path.basename(self.file_path)}: {decoded_line}")
            exit_code = process.wait()
            if exit_code == 0:
                self.finished.emit(f"✅ Done: {os.path.basename(output_file)}")
            else:
                self.finished.emit(f"❌ FFmpeg failed for: {os.path.basename(self.file_path)} (exit code {exit_code})")
        except Exception as e:
            self.finished.emit(f"❌ Exception: {str(e)}")
