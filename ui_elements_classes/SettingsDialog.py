from PyQt5.uic import loadUiType
import numpy as np  # for evaluation of ratio
from utils.global_vars import *

Ui_SettingsDialog, QDialog = loadUiType('./ui_elements/QtUI/SettingsDialog.ui')


class SettingsDialog(QDialog, Ui_SettingsDialog):
    def __init__(self, parent=None, parameters=None, **kwargs):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Settings")
        self.cb_ftype.addItems(supportedLoadFormats)
        self.cb_dtype.addItems(supportedDataTypes)
        self.result = None

        self.cb_ftype.setCurrentText(kwargs["ftype"])
        self.cb_dtype.setCurrentText(parameters.dtype)
        self.sb_header.setValue(parameters.header)
        self.sb_width.setValue(parameters.width)
        self.sb_height.setValue(parameters.height)

        self.buttonBox.accepted.connect(self.accept)

    def accept(self):
        self.result = {
            "ftype": self.cb_ftype.currentText(),
            "dtype": self.cb_dtype.currentText(),
            "width": self.sb_width.value(),
            "height": self.sb_height.value(),
            "header": self.sb_header.value(),
            "show_axes": self.cb_show_axes.isChecked(),
            "ratio": eval(self.le_ratio.text())
        }
        super().accept()
