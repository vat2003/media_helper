import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QPushButton, QLineEdit, QFileDialog,
    QComboBox, QTextEdit, QLabel, QHBoxLayout, QFrame
)
from workers.merge_worker_threaded import MergeWorkerThreaded


class MergeForm(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Title
        title = QLabel("🎞️ Ghép Video/Hình + Âm Thanh")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        main_layout.addWidget(title)

        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        self.video_or_image_input = QLineEdit()
        self.audio_input = QLineEdit()
        self.output_path = QLineEdit()
        self.resolution_box = QComboBox()
        self.gpu_mode_box = QComboBox()

        self.resolution_box.addItems(["1280x720", "1920x1080", "2560x1440", "3840x2160"])
        self.gpu_mode_box.addItems(["CPU", "GPU (NVIDIA)"])

        form_layout.addRow("📁 Video hoặc Ảnh:", self.file_picker(self.video_or_image_input))
        form_layout.addRow("🎵 File âm thanh:", self.file_picker(self.audio_input))
        form_layout.addRow("💾 Đường dẫn lưu:", self.file_picker(self.output_path, save=True))
        form_layout.addRow("📐 Độ phân giải:", self.resolution_box)
        form_layout.addRow("⚙️ Chế độ mã hoá:", self.gpu_mode_box)

        main_layout.addLayout(form_layout)

        # Run button
        self.run_button = QPushButton("🚀 Bắt đầu ghép")
        self.run_button.setStyleSheet("""
            padding: 10px;
            font-weight: bold;
            background-color: #007bff;
            color: white;
            border-radius: 6px;
        """)
        self.run_button.clicked.connect(self.start_merge)
        main_layout.addWidget(self.run_button)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        # Log output
        main_layout.addWidget(QLabel("📜 Logs:"))

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMinimumHeight(100)
        self.log_output.setStyleSheet("""
            QTextEdit {
                font-family: Consolas, monospace;
                font-size: 12px;
                background-color: #fdfdfd;
                border: 1px solid #ccc;
                padding: 6px;
            }
        """)
        main_layout.addWidget(self.log_output)

        main_layout.addStretch()

    def file_picker(self, lineedit, save=False):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        browse_btn = QPushButton("📂")
        browse_btn.setFixedWidth(30)

        def choose():
            if save:
                path, _ = QFileDialog.getSaveFileName(self, "Save As", "", "MP4 Files (*.mp4);;All Files (*)")
            else:
                path, _ = QFileDialog.getOpenFileName(self, "Choose File", "", "All Files (*)")
            if path:
                lineedit.setText(path)

        browse_btn.clicked.connect(choose)

        layout.addWidget(lineedit, 1)
        layout.addWidget(browse_btn, 0)

        return container

    def log(self, msg):
        self.log_output.append(msg)

    def start_merge(self):
        v = self.video_or_image_input.text().strip()
        a = self.audio_input.text().strip()
        o = self.output_path.text().strip()
        res = self.resolution_box.currentText()
        use_gpu = self.gpu_mode_box.currentText() == "GPU (NVIDIA)"

        if not all([v, a, o]):
            self.log("⚠️ Vui lòng điền đầy đủ đường dẫn input/output.")
            return

        self.run_button.setEnabled(False)

        self.worker = MergeWorkerThreaded(
            video_path=v,
            audio_path=a,
            output_path=o,
            resolution=res,
            use_gpu=use_gpu,
            on_log=self.log,
            on_finish=self.on_worker_finished
        )
        self.worker.start()

    def on_worker_finished(self, message):
        self.log(message)
        self.run_button.setEnabled(True)
