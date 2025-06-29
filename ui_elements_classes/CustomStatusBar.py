from PyQt5.QtWidgets import QStatusBar, QProgressBar


class CustomStatusBar(QStatusBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.progress_bar = QProgressBar(self)
        self.addPermanentWidget(self.progress_bar, 0)
        self.progress_bar.setMaximum(0)
        self.progress_bar.setVisible(False)

    def start_progress(self, steps):
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(self.progress_bar.maximum() + steps - 1)

    def update_progress(self, steps):
        self.progress_bar.setValue(steps)
        if self.progress_bar.value() == self.progress_bar.maximum():
            self.progress_bar.reset()

    def add_progress(self, steps=1):
        self.progress_bar.setValue(self.progress_bar.value() + steps)
        if self.progress_bar.value() == self.progress_bar.maximum():
            self.progress_bar.setMaximum(0)
            self.progress_bar.reset()
            self.progress_bar.setVisible(False)
