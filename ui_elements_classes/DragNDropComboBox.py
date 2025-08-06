from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QComboBox

from utils import create_item


class DragNDropComboBox(QComboBox):
    remove_items = pyqtSignal(list, name="removeItems")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def get_custom_item(self, index):
        idx = self.model().index(index, 0)
        return self.model().itemFromIndex(idx)

    def set_current_index_by_im_id(self, im_id):
        row = 0
        for row in range(self.model().rowCount()):
            item = self.model().item(row, 0)
            if item.data(Qt.UserRole, ) == im_id:
                break
        self.setCurrentIndex(row)

    def get_current_item(self):
        return self.get_custom_item(self.currentIndex())

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
