from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QTreeView
from PyQt5.QtCore import Qt


class CustomTreeView(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.model = QStandardItemModel()
        self.setModel(self.model)

        self.setDragDropMode(self.InternalMove)

    def add_item(self, group, text):
        group_item = self.find_group(group)
        if not group_item:
            group_item = QStandardItem(group)
            self.model.appendRow(group_item)

        item = QStandardItem(text)
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)
        group_item.appendRow(item)

    def find_group(self, group):
        for row in range(self.model.rowCount()):
            item = self.model.item(row)
            if item.text() == group:
                return item
        return None

    def dropEvent(self, event):
        source_item = self.model.itemFromIndex(self.indexAt(event.pos()))
        dest_item = self.model.itemFromIndex(self.indexAt(event.pos()))

        if source_item and dest_item:
            # Move the item to the destination group
            dest_group_item = dest_item.parent()
            if dest_group_item:
                dest_group_item.appendRow(source_item.takeRow(source_item.row()))

        super().dropEvent(event)
