from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit,
    QComboBox, QHBoxLayout, QSizePolicy, QFrame
)
from widgets.file_list_widget import DraggableListWidget
from workers.ffmpeg_worker import FFmpegWorker


class BasicTaskTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Title
        title = QLabel("🎬 Xử Lý Cơ Bản với FFmpeg")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        main_layout.addWidget(title)

        # File List Section
        main_layout.addWidget(QLabel("📂 Kéo và thả file video vào bên dưới:"))

        self.file_list = DraggableListWidget()
        self.file_list.setMinimumHeight(80)
        main_layout.addWidget(self.file_list)

        self.clear_button = QPushButton("🗑 Xoá danh sách file")
        self.clear_button.setStyleSheet("padding: 6px 14px;")
        self.clear_button.clicked.connect(self.clear_file_list)
        main_layout.addWidget(self.clear_button)

        # Preset Section
        main_layout.addWidget(QLabel("⚙️ Chọn tác vụ FFmpeg:"))

        self.preset_box = QComboBox()
        self.preset_box.addItems([
            "Convert to MP4",
            "Extract Audio",
            "Resize 720p",
            "Generate Tracklist"
        ])
        self.preset_box.setStyleSheet("padding: 6px;")
        main_layout.addWidget(self.preset_box)

        # Run Button
        self.start_button = QPushButton("🚀 Bắt đầu xử lý")
        self.start_button.setStyleSheet("""
            padding: 10px;
            font-weight: bold;
            background-color: #28a745;
            color: white;
            border-radius: 6px;
        """)
        self.start_button.clicked.connect(self.start_processing)
        main_layout.addWidget(self.start_button)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        # Log Box
        main_layout.addWidget(QLabel("📜 Logs:"))

        self.progress_text = QTextEdit()
        self.progress_text.setReadOnly(True)
        self.progress_text.setMinimumHeight(100)
        self.progress_text.setStyleSheet("""
            QTextEdit {
                font-family: Consolas, monospace;
                font-size: 12px;
                background-color: #fdfdfd;
                border: 1px solid #ccc;
                padding: 6px;
            }
        """)
        main_layout.addWidget(self.progress_text)

        main_layout.addStretch()

        # Thread List
        self.threads = []

    def log_message(self, message):
        self.progress_text.append(message)

    def clear_file_list(self):
        self.file_list.clear()
        self.log_message("🧹 Danh sách file đã được xoá.")

    def start_processing(self):
        preset = self.preset_box.currentText()

        for i in range(self.file_list.count()):
            file_path = self.file_list.item(i).text()

            if preset == "Generate Tracklist" and not file_path.lower().endswith(".txt"):
                self.log_message(f"❌ File '{file_path}' không phải file .txt cho tracklist.")
                continue

            if preset != "Generate Tracklist" and not file_path.lower().endswith(".mp4"):
                self.log_message(f"❌ File '{file_path}' không phải video mp4 phù hợp với preset '{preset}'.")
                continue

            worker = FFmpegWorker(file_path, preset)
            worker.progress.connect(self.log_message)
            worker.finished.connect(self.log_message)
            self.threads.append(worker)
            worker.start()
