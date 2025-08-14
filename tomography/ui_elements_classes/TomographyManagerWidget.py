from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.uic import loadUiType
from .XRD1611Widget import XRD1611Widget
from .SoloistWidget import SoloistWidget
from utils import LogTypes
from tomography.utils import get_config
from ui_elements import icon_app

config = get_config()["Server"]
detectors = config["detectors"].split(" ")
tables = config["tables"].split(" ")

UI_TomographyManagerWidget, QWidget = loadUiType('./tomography/ui_elements/TomographyManagerWidget.ui')

class TomographyManagerWidget(QWidget, UI_TomographyManagerWidget):
    new_image = pyqtSignal(tuple, name='new_image')
    worker_tabs = {}

    def __init__(self, parent=None, main_window=None):
        self.main_window = main_window
        super(TomographyManagerWidget, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Tomography Manager")
        self.setWindowIcon(QIcon(icon_app))

    def new_message(self, name, *message):
        if name == "TomographyManager":
            status_code = message[0]
            message = message[1]
            self.log(message, LogTypes.Log if status_code == 0 else LogTypes.Error)
        elif name in self.worker_tabs:
            self.worker_tabs[name].new_message(*message)
        else:
            print(message)

    def log(self, text, log_type=LogTypes.Log):
        if log_type == LogTypes.Log:
            text = f"<font color='green'>{text}</font>"
        elif log_type == LogTypes.Warning:
            text = f"<font color='yellow'>Warning: {text}</font>"
        elif log_type == LogTypes.Error:
            text = f"<font color='red'>{text}</font>"
        self.log_widget.append(text)

    def worker_initialized(self, name, queue):
        if name in detectors:
            dt = globals()[f"{name}Widget"](self, queue)
            self.worker_tabs[name] = dt
            dt.new_image.connect(self.new_image)
            self.tw_detectors.addTab(self.worker_tabs[name], name)
        elif name in tables:
            tw = globals()[f"{name}Widget"](self, queue)
            self.layout().insertWidget(0, tw)
            self.worker_tabs[name] = tw



