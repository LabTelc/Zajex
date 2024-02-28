from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QListView

from utils.global_vars import item_type


class DragNDropListView(QListView):
    itemChanged = pyqtSignal(name="itemChanged")

    def __init__(self, parent=None):
        super(DragNDropListView, self).__init__(parent)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.model = None

    def set_custom_model(self, custom_model):
        self.model = custom_model
        self.setModel(custom_model)

    def dragEnterEvent(self, event, **kwargs):
        if event.mimeData().hasUrls() or event.mimeData().hasFormat(item_type):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event, **kwargs):
        if event.mimeData().hasUrls() or event.mimeData().hasFormat(item_type):
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event, **kwargs):
        if event.mimeData().hasUrls():  # loading new files
            urls = event.mimeData().urls()
            file_paths = [url.toLocalFile() for url in urls]
            self.window().open_files(file_paths, self.objectName().split("_")[-1])
            event.accept()

        elif event.mimeData().hasFormat(item_type):  # moving between list views
            selected_indexes = event.source().selectedIndexes()
            for index in reversed(selected_indexes):  # to avoid index shifting
                item = event.source().model.takeRow(index.row())
                if len(item) > 0:
                    self.model.insertRow(0, item)

            event.source().itemChanged.emit()
            self.itemChanged.emit()
            event.accept()

        else:
            event.ignore()

    def get_custom_item(self, index):
        return self.model.itemFromIndex(index)

    def keyPressEvent(self, event):  # for deleting items
        if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            selected_indexes = self.selectedIndexes()
            for index in selected_indexes:
                self.model.removeRow(index.row())
            self.itemChanged.emit()
        else:
            super().keyPressEvent(event)

    def remove_item(self, im_id):  # TODO use takeRow
        for row in range(self.model.rowCount()):
            item = self.model.item(row, 0)
            if item.data(Qt.UserRole, ) == im_id:
                self.model.removeRow(row)
                break
