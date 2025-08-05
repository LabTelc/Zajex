from PyQt5.QtWidgets import QStyle
from PyQt5.uic import loadUiType

from utils.global_vars import *

Ui_SettingsDialog, QDialog = loadUiType('./ui_elements/QtUI/BatchDialog.ui')


class BatchDialog(QDialog, Ui_SettingsDialog):
    def __init__(self, parent=None, parameters=None, **kwargs):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Settings")
        self.cb_ftype.addItems(supportedLoadFormats[:-1])
        self.cb_dtype.addItems(supportedDataTypes)
        self.tb_pick_location.setIcon(self.style().standardIcon(QStyle.SP_DirIcon))
        self.result = None

        self.buttonBox.accepted.connect(self.accept)
