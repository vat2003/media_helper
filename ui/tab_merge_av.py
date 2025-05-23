from PyQt5.QtWidgets import QWidget, QVBoxLayout
from widgets.form_merge_av import MergeForm


class MergeAudioVideoTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(MergeForm())
