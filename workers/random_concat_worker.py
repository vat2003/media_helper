import os
import random
import subprocess
import time
from PyQt5.QtCore import QThread, pyqtSignal

def get_media_files(input_folder):
    supported_extensions = ('.mp4', '.mkv', '.avi', '.mov', '.mp3', '.wav', '.aac')
    return [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.lower().endswith(supported_extensions)]

def get_duration(file_path):
    try:
        result = subprocess.run([
            'ffprobe', '-v', 'error', '-show_entries',
            'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file_path
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return float(result.stdout.strip())
    except:
        return 0

def seconds_to_hhmmss(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"[{hours:02}:{minutes:02}:{secs:02}]"

def create_tracklist(selected_files, tracklist_path):
    current_time = 0
    with open(tracklist_path, 'w', encoding='utf-8') as f:
        for file_path in selected_files:
            filename_with_ext  = os.path.basename(file_path)
            filename = os.path.splitext(filename_with_ext)[0]  # ❗ Loại bỏ đuôi .mp4, .mp3,...
            f.write(f"{seconds_to_hhmmss(current_time)} {filename}\n")
            current_time += get_duration(file_path)

def create_file_list_file(file_list, temp_list_path):
    with open(temp_list_path, 'w', encoding='utf-8') as f:
        for file_path in file_list:
            f.write(f"file '{file_path}'\n")

class RandomConcatWorker(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(str)

    def __init__(self, input_folder, output_folder, files_per_concat, num_outputs):
        super().__init__()
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.files_per_concat = files_per_concat
        self.num_outputs = num_outputs

    def run(self):
        os.makedirs(self.output_folder, exist_ok=True)
        media_files = get_media_files(self.input_folder)

        if len(media_files) < self.files_per_concat:
            self.progress.emit("❗ Không đủ file trong thư mục để ghép.")
            return

        timestamp = str(int(time.time()))

        for i in range(1, self.num_outputs + 1):
            selected = random.sample(media_files, self.files_per_concat)
            output_base = f"{timestamp}_output_{i}"
            output_extension = ".mp4" if selected[0].lower().endswith(('.mp4', '.mkv', '.avi', '.mov')) else ".mp3"

            output_path = os.path.join(self.output_folder, output_base + output_extension)
            tracklist_path = os.path.join(self.output_folder, output_base + "_tracklist.txt")
            temp_list_path = os.path.join(self.input_folder, 'temp_list.txt')

            create_file_list_file(selected, temp_list_path)
            command = [
                'ffmpeg', '-hide_banner', '-fflags', '+genpts',
                '-f', 'concat', '-safe', '0', '-i', temp_list_path,
                '-c', 'copy', '-y', output_path
            ]

            try:
                subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.progress.emit(f"✅ Output: {output_path}")
                create_tracklist(selected, tracklist_path)
                self.progress.emit(f"📝 Tracklist: {tracklist_path}")
            except subprocess.CalledProcessError as e:
                self.progress.emit(f"❌ Lỗi ghép file {i}: {str(e)}")
            finally:
                if os.path.exists(temp_list_path):
                    os.remove(temp_list_path)

        self.finished.emit("✅ Hoàn tất ghép tất cả file.")
