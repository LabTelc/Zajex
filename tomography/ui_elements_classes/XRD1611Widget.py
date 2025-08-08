from PyQt5.QtGui import QIcon
from PyQt5.uic import loadUiType
from ui_elements import icon_load, icon_add

UI_XRD1611Widget, QWidget = loadUiType('./tomography/ui_elements/XRD1611.ui')

class XRD1611Widget(QWidget, UI_XRD1611Widget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        for corr in ["ob", "df", "bpm"]:
            getattr(self, f"tb_{corr}_file").setIcon(QIcon(icon_load))
            getattr(self, f"tb_{corr}_img").setIcon(QIcon(icon_add))
