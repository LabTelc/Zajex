from PyQt5.QtCore import pyqtSignal, QTimer, Qt
from PyQt5.QtWidgets import QComboBox


class CustomComboBox(QComboBox):
    save_signal = pyqtSignal(str, name='name')

    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._hold_handler)
        self.timer.setSingleShot(True)

    def mousePressEvent(self, event, QMouseEvent=None):
        if event.button() == Qt.LeftButton:
            self.timer.start(500)
            super().mousePressEvent(event)
            self.hidePopup()
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event, QMouseEvent=None):
        if event.button() == Qt.LeftButton:
            self.timer.stop()
            self.save_signal.emit(self.currentText())
        else:
            super().mouseReleaseEvent(event)

    def _hold_handler(self):
        self.showPopup()
