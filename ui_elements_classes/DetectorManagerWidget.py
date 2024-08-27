from PyQt5.QtWidgets import QWidget


class DetectorManagerWidget(QWidget):
    def __init__(self, parent=None, dm=None):
        super(DetectorManagerWidget, self).__init__(parent)
        self.dm_thread = dm


