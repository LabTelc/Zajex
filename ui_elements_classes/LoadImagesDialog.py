from PyQt5.uic import loadUiType

Ui_SettingsDialog, QDialog = loadUiType('./ui_elements/LoadImagesDialog.ui')


class LoadImagesDialog(QDialog, Ui_SettingsDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Select group")
        self.result = None

        self.buttonBox.accepted.connect(self.accept)

    def accept(self):
        self.result = self.cb_group.currentText().lower()
        super().accept()
