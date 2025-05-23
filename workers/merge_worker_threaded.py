import subprocess
import os
import threading

class MergeWorkerThreaded:
    def __init__(self, video_path, audio_path, output_path, resolution, use_gpu, on_log=None, on_finish=None):
        self.video_path = video_path
        self.audio_path = audio_path
        self.output_path = output_path
        self.resolution = resolution
        self.use_gpu = use_gpu
        self.on_log = on_log
        self.on_finish = on_finish

    def start(self):
        thread = threading.Thread(target=self.run)
        thread.daemon = True  # Cho phép thoát app mà không treo
        thread.start()

    def run(self):
        scale_filter = f"scale={self.resolution},format=yuv420p"
        is_image = self.video_path.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.webp'))

        loop_input = ['-loop', '1'] if is_image else []

        encoder = ['-c:v', 'h264_nvenc'] if self.use_gpu else ['-c:v', 'libx264']

        command = [
            'ffmpeg',
            '-hide_banner',
            '-loglevel', 'warning',
            *loop_input,
            '-i', self.video_path,
            '-i', self.audio_path,
            '-map', '0:v:0',  # lấy video từ input 0
            '-map', '1:a:0',  # lấy audio từ input 1
            *encoder,
            '-preset', 'medium',
            '-vf', scale_filter,
            '-c:a', 'copy',
            '-shortest',
            '-y',
            self.output_path
        ]

        if self.on_log:
            self.on_log(f"🟢 Running...........................")

        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in process.stdout:
                decoded = line.decode('utf-8', errors='replace').strip()
                if self.on_log:
                    self.on_log(decoded)
            exit_code = process.wait()

            if exit_code == 0:
                if self.on_finish:
                    self.on_finish(f"✅ Merge completed ==> {self.output_path}")
            else:
                if self.on_finish:
                    self.on_finish("❌ Merge failed. Please check the log above.")

        except Exception as e:
            if self.on_log:
                self.on_log(f"❌ Error: {e}")
            if self.on_finish:
                self.on_finish("❌ Merge failed.")
