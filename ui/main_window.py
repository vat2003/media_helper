from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from ui.tab_basic_tasks import BasicTaskTab
from ui.tab_merge_av import MergeAudioVideoTab
from ui.tab_random_concat import RandomConcatTab


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FFmpeg Video Processor")
        self.resize(500, 500)
        layout = QVBoxLayout(self)

        tabs = QTabWidget()
        tabs.addTab(BasicTaskTab(), "Basic Tasks")
        tabs.addTab(MergeAudioVideoTab(), "Merge Image/Video + Audio")
        tabs.addTab(RandomConcatTab(), "Random Concat")

        layout.addWidget(tabs)
