from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QListView


class DragNDropListView(QListView):
    def __init__(self, parent=None):
        super(DragNDropListView, self).__init__(parent)
        self.setAcceptDrops(True)
        self.model = None
        self.doubleClicked.connect(self.show_image)

    def set_custom_model(self, custom_model):
        self.model = custom_model
        self.setModel(custom_model)

    def dragEnterEvent(self, event, **kwargs):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event, **kwargs):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event, **kwargs):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            file_paths = [url.toLocalFile() for url in urls]
            self.window().open_files(file_paths, self.objectName().split("_")[-1])
            event.accept()
        else:
            event.ignore()

    def show_image(self, index):
        item = self.model.itemFromIndex(index)
        if item is not None:
            self.window()._cb_images_handler(item.data(Qt.UserRole))

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            selected_indexes = self.selectedIndexes()
            for index in selected_indexes:
                self.model.removeRow(index)
        else:
            super().keyPressEvent(event)