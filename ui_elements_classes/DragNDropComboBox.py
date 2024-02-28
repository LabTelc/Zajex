from PyQt5.QtCore import Qt, QMimeData, QTimer, pyqtSignal
from PyQt5.QtGui import QDrag, QStandardItem
from PyQt5.QtWidgets import QComboBox, QApplication


class DragNDropComboBox(QComboBox):
    item_changed = pyqtSignal(name="itemChanged")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.start_drag)
        self.setAcceptDrops(True)
        self.model = None

    def set_custom_model(self, custom_model):
        self.model = custom_model
        self.setModel(custom_model)

    def add_item(self, item):
        self.model.appendRow(item)

    def get_custom_item(self, index):
        idx = self.model.index(index, 0)
        return self.model.itemFromIndex(idx)

    def get_current_item(self):
        return self.get_custom_item(self.currentIndex())

    def mousePressEvent(self, event, **kwargs):
        if event.button() == Qt.LeftButton:
            self.startPos = event.pos()
            self.timer.start(200)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event, **kwargs):
        if event.button() == Qt.LeftButton and self.timer.isActive():
            self.timer.stop()
            self.hidePopup()
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if not hasattr(self, 'startPos'):
            return

        distance = (event.pos() - self.startPos).manhattanLength()
        if distance > QApplication.startDragDistance():
            self.start_drag()

    def start_drag(self):
        current_index = self.currentIndex()
        if current_index < 0:
            return
        idx = self.model.index(current_index, 0)
        item = self.model.itemFromIndex(idx)
        im_id = item.data(Qt.UserRole, )

        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(str(im_id))
        drag.setMimeData(mime_data)
        drag.exec_(Qt.MoveAction)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():    # text ~ moving items between combo boxes
            event.acceptProposedAction()  # urls ~ loading new files

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():    # text ~ moving items between combo boxes
            event.acceptProposedAction()  # urls ~ loading new files

    def dropEvent(self, event):
        if event.mimeData().hasUrls():  # loading new files
            urls = event.mimeData().urls()
            file_paths = [url.toLocalFile() for url in urls]
            self.window().open_files(file_paths, self.objectName().split("_")[-1])
            event.accept()
        elif event.mimeData().hasText():  # moving between combo boxes
            im_id = int(event.mimeData().text())
            event.source().remove_item(im_id)
            event.source().item_changed.emit()

            item = QStandardItem()
            img = self.window().images[im_id]
            item.setToolTip(img.filepath)
            item.setText(img.filepath.split("/")[-1])
            item.setData(im_id, Qt.UserRole)
            self.model.appendRow(item)

            event.acceptProposedAction()
            self.item_changed.emit()
        else:
            event.ignore()

    def remove_item(self, im_id):  # TODO use takeRow
        for row in range(self.model.rowCount()):
            item = self.model.item(row, 0)
            if item.data(Qt.UserRole, ) == im_id:
                self.model.removeRow(row)
                break
