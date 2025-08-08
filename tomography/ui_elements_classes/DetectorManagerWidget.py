from PyQt5.QtCore import pyqtSignal
from PyQt5.uic import loadUiType
from .XRD1611Widget import XRD1611Widget

UI_DetectorManagerWidget, QWidget = loadUiType('./tomography/ui_elements/TomographyManagerWidget.ui')

class DetectorManagerWidget(QWidget, UI_DetectorManagerWidget):
    new_message = pyqtSignal(tuple, name="new_message")
    detector_tabs = {}

    def __init__(self, parent=None, dm=None):
        super(DetectorManagerWidget, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Detector Manager")
        self.dm_thread = dm

    def _add_tab(self, name):
        dt = globals()[f"{name}Widget"](self)
        self.detector_tabs[name] = dt
        self.tw_detectors.addTab(self.detector_tabs[name], name)

    def new_message(self, message, log_type):
        if "DetectorManager" in message:
            self.new_message.emit((message, log_type))
        else:
            pass


    def post_command(self, args):
        det, cmd, value = args
        self.dm_thread.queues.put((det, (cmd, value)))

    def detector_initialized(self, name):
        self._add_tab(name)



