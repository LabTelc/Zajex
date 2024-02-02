from PyQt5.QtGui import QStandardItem


class CustomStandardItem(QStandardItem):
    def __init__(self, parent=None, im_id=None):
        super().__init__(parent)
        self.im_id = im_id
