from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog,
    QHBoxLayout, QSpinBox, QGroupBox, QFormLayout, QFrame, QSizePolicy,
    QPlainTextEdit
)
from workers.random_concat_worker import RandomConcatWorker


class RandomConcatTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Title
        title = QLabel("🎞️ Ghép File Media Ngẫu Nhiên")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        main_layout.addWidget(title)

        # Folder Section
        folder_section = QHBoxLayout()
        self.folder_label = QLabel("❌ Chưa chọn thư mục")
        self.folder_label.setStyleSheet("color: gray;")
        self.folder_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.btn_choose_input = QPushButton("📂 Chọn thư mục chứa file")
        self.btn_choose_input.setStyleSheet("padding: 6px 14px;")
        self.btn_choose_input.clicked.connect(self.choose_input)

        folder_section.addWidget(self.folder_label)
        folder_section.addWidget(self.btn_choose_input)
        main_layout.addLayout(folder_section)

        # Options Section
        options_group = QGroupBox("⚙️ Tùy chọn")
        options_layout = QFormLayout()

        self.files_per_spin = QSpinBox()
        self.files_per_spin.setRange(1, 500)
        self.files_per_spin.setValue(5)

        self.num_outputs_spin = QSpinBox()
        self.num_outputs_spin.setRange(1, 100)
        self.num_outputs_spin.setValue(2)

        options_layout.addRow("🔢 Số file mỗi lần ghép:", self.files_per_spin)
        options_layout.addRow("🧾 Số file đầu ra:", self.num_outputs_spin)

        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)

        # Run Button
        self.btn_run = QPushButton("🚀 Bắt đầu ghép")
        self.btn_run.setStyleSheet("""
            padding: 10px;
            font-weight: bold;
            background-color: #007acc;
            color: white;
            border-radius: 6px;
        """)
        self.btn_run.clicked.connect(self.run_worker)
        main_layout.addWidget(self.btn_run)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        # Log Box
        main_layout.addWidget(QLabel("📜 Logs:"))

        self.log_box = QPlainTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setPlaceholderText("Logs sẽ hiển thị ở đây...")
        self.log_box.setMinimumHeight(100)
        self.log_box.setStyleSheet("""
            QPlainTextEdit {
                font-family: Consolas, monospace;
                font-size: 12px;
                background-color: #fdfdfd;
                border: 1px solid #ccc;
                padding: 6px;
            }
        """)
        main_layout.addWidget(self.log_box)

        main_layout.addStretch()

    def choose_input(self):
        folder = QFileDialog.getExistingDirectory(self, "Chọn thư mục input")
        if folder:
            self.input_folder = folder
            self.output_folder = folder + "_output"
            self.folder_label.setText(f"📁 {folder}")
            self.folder_label.setStyleSheet("color: green;")

    def log_message(self, msg):
        self.log_box.appendPlainText(msg)

    def run_worker(self):
        if not hasattr(self, 'input_folder') or not self.input_folder:
            self.log_message("⚠️ Vui lòng chọn thư mục input.")
            return

        self.log_box.appendPlainText("⏳ Đang xử lý...")

        self.worker = RandomConcatWorker(
            self.input_folder,
            self.output_folder,
            self.files_per_spin.value(),
            self.num_outputs_spin.value()
        )
        self.worker.progress.connect(self.log_message)
        self.worker.finished.connect(self.log_message)
        self.worker.start()
