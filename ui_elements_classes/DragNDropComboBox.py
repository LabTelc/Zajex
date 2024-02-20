from PyQt5.QtGui import QStandardItemModel, QDrag, QStandardItem
from PyQt5.QtWidgets import QComboBox, QApplication
from PyQt5.QtCore import Qt, QMimeData, QTimer, pyqtSignal


class DragNDropComboBox(QComboBox):
    item_changed = pyqtSignal(name="itemChanged")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = QStandardItemModel(self)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.start_drag)
        self.setModel(self.model)
        self.setAcceptDrops(True)

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
            self.timer.start(300)
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
        im_id = item.data(Qt.UserRole)
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(str(im_id))
        drag.setMimeData(mime_data)
        drag.exec_(Qt.MoveAction)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            im_id = int(event.mimeData().text())
            event.source().remove_item(im_id)
            event.source().item_changed.emit()

            # If dropping within the same combo box, move the item
            if event.source() == self:
                source_index = self.currentIndex()
                source_item = self.model.itemFromIndex(source_index)
                source_im_id = source_item.im_id
                if source_im_id == im_id:
                    return
                source_item.setText(str(im_id))

            # If dropping from another combo box, add a new item
            else:
                item = QStandardItem()
                _, filepath = self.window().images[im_id]
                item.setToolTip(filepath)
                item.setText(filepath.split("/")[-1])
                item.setData(im_id, Qt.UserRole)
                self.model.appendRow(item)

            event.acceptProposedAction()
            self.item_changed.emit()

    def remove_item(self, im_id):
        for row in range(self.model.rowCount()):
            item = self.model.item(row, 0)
            if item.data(Qt.UserRole) == im_id:
                self.model.removeRow(row)
                break
