from PyQt5.QtCore import QAbstractListModel, Qt


class InternalModel(QAbstractListModel):
    def __init__(self, data=None, parent=None):
        super().__init__(parent)
        self._data = data or []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self._data[index.row()]

    def rowCount(self, index):
        return len(self._data)

    def appendRow(self, row):
        self._data.append(row)
