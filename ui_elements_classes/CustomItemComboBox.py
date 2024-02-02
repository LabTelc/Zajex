from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QComboBox


class CustomItemComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = QStandardItemModel(self)
        self.setModel(self.model)

    def addCustomItem(self, item):
        self.model.appendRow(item)

    def getCustomItem(self, index):
        idx = self.model.index(index, 0)
        return self.model.itemFromIndex(idx)