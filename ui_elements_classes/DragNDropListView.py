from PyQt5.QtCore import Qt, pyqtSignal, QMimeData
from PyQt5.QtWidgets import QListView
from PyQt5.QtGui import QDrag

from utils import create_item


class DragNDropListView(QListView):
    remove_items = pyqtSignal(list, name="removeItems")
    delete_items = pyqtSignal(list, name="deleteItems")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.moving_method = None

    def set_move_mode(self, mode="copy"):
        """
        Method for switching between copy and move in moving items between list views
        :param mode: copy or move
        """
        if mode == "copy":
            self.moving_method = self.copy_method
        elif mode == "move":
            self.moving_method = self.model().takeRow

    def copy_method(self, row):
        item = self.model().item(row)
        return item.clone()

    def dragEnterEvent(self, event, **kwargs):
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event, **kwargs):
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

    def startDrag(self, supported_actions, qt_drop_actions=None, qt_drop_action=None):
        selected = self.selectedIndexes()
        selected = [self.model().itemFromIndex(index).data(Qt.UserRole, ) for index in selected]

        mime_data = QMimeData()
        mime_data.setText(",".join(str(im_id) for im_id in selected)) # using text to transfer IDs

        drag = QDrag(self)
        drag.setMimeData(mime_data)
        drag.exec_(supported_actions)

    def dropEvent(self, event, **kwargs):
        if event.mimeData().hasUrls():  # loading new files
            urls = event.mimeData().urls()
            file_paths = [url.toLocalFile() for url in urls]
            self.window().open_files(file_paths, self.objectName().split("_")[-1])
            event.accept()

        elif event.mimeData().hasText():  # moving
            selected_ids = [int(im_id) for im_id in event.mimeData().text().split(",")]
            self.remove_items.emit(selected_ids)
            slot = self.objectName().split("_")[-1]
            for im_id in selected_ids:
                im = self.window().images[im_id]
                im.slot = slot
                item = create_item(im, im_id)
                self.model().insertRow(0, item)

            event.accept()
        else:
            event.ignore()

    def get_custom_item(self, index):
        return self.model().itemFromIndex(index)

    def keyPressEvent(self, event):  # for deleting items
        if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            selected = self.selectedIndexes()
            selected_ids = [self.model().itemFromIndex(index).data(Qt.UserRole, ) for index in selected]
            self.remove_items.emit(selected_ids)
            self.delete_items.emit(selected_ids)
        else:
            super().keyPressEvent(event)
