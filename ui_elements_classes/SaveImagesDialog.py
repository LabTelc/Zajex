import os

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QStyle, QFileDialog, QDialogButtonBox
from PyQt5.uic import loadUiType

from utils.global_vars import *

Ui_SettingsDialog, QDialog = loadUiType('./ui_elements/QtUI/SaveImagesDialog.ui')


class SaveImagesDialog(QDialog, Ui_SettingsDialog):
    save_signal = pyqtSignal(name="save")

    def __init__(self, parent=None, models=None, saving_queue=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Select images to save")
        self.saving_queue = saving_queue

        self.model = QStandardItemModel()
        self.lw_a.set_custom_model(self.clone_model(models["a"]))
        self.lw_a.setAcceptDrops(False)
        self.lw_b.set_custom_model(self.clone_model(models["b"]))
        self.lw_b.setAcceptDrops(False)
        self.lw_c.set_custom_model(self.clone_model(models["c"]))
        self.lw_c.setAcceptDrops(False)
        self.lw_d.set_custom_model(self.clone_model(models["d"]))
        self.lw_d.setAcceptDrops(False)
        self.lw_s.set_custom_model(self.model)
        self.models = {
            "a": self.lw_a,
            "b": self.lw_b,
            "c": self.lw_c,
            "d": self.lw_d,
            "s": self.lw_s
        }
        # for model in self.models.values():
        #     model.set_move_mode("copy")

        self.cb_ftype.addItems(supportedSaveFormats)
        self.cb_dtype.addItems(supportedDataTypesByFileType[self.cb_ftype.currentText()])
        self.cb_ftype.currentIndexChanged.connect(self._cb_ftype_handler)
        # self.cb_remove.clicked.connect(self._cb_remove_handler)
        self.buttonBox.clicked.connect(self.save_images)
        self.pb_pick_location.clicked.connect(self.pick_location)
        self.pb_pick_location.setIcon(self.style().standardIcon(QStyle.SP_DirIcon))
        self.le_output_path.setText(os.getcwd())

        self.result = None

    # def _cb_remove_handler(self):
    #     if self.cb_remove.isChecked():
    #         for model in self.models.values():
    #             model.set_move_mode("move")
    #     else:
    #         for model in self.models.values():
    #             model.set_move_mode("copy")

    @staticmethod
    def clone_model(model):
        clone = QStandardItemModel()
        for row in range(model.rowCount()):
            item = model.item(row)
            cloned_item = item.clone()
            clone.appendRow(cloned_item)
        return clone

    def pick_location(self):
        path = QFileDialog.getExistingDirectory(self, "Select a Folder", os.getcwd())
        if path is not None:
            self.le_output_path.setText(path)

    def save_images(self, button):
        if self.buttonBox.buttonRole(button) == QDialogButtonBox.AcceptRole:
            kwargs = {"dtype": self.cb_dtype.currentText()}

            if self.cb_remove.isChecked():
                kwargs["remove"] = True
                self.result = {key: self.models[key].model for key in self.models}

            for row in range(self.model.rowCount()):
                item = self.model.item(row)
                im_id = item.data(Qt.UserRole)
                ftype = self.cb_ftype.currentText()
                filepath = self.le_output_path.text()
                self.saving_queue.put((im_id, ftype, filepath, kwargs))

    def _cb_ftype_handler(self):
        self.cb_dtype.clear()
        self.cb_dtype.addItems(supportedDataTypesByFileType[self.cb_ftype.currentText()])
