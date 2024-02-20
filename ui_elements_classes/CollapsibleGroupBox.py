from PyQt5.QtCore import QParallelAnimationGroup, QPropertyAnimation, QAbstractAnimation, pyqtSlot
from PyQt5.QtWidgets import QGroupBox, QSizePolicy


class CollapsibleGroupBox(QGroupBox):
    def __init__(self, parent=None):
        super(CollapsibleGroupBox, self).__init__(parent)
        self.setStyleSheet("""
                        QGroupBox::indicator {
                            width: 10px;
                            height: 10px;
                        }
                        QGroupBox::indicator:checked {
                            image: url(./ui_elements/arrow_down.png);
                        }
                        QGroupBox::indicator:unchecked {
                            image: url(./ui_elements/arrow_right.png);
                        }
                    """)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toggle_animation = QParallelAnimationGroup(self)
        self.toggle_animation.addAnimation(
            QPropertyAnimation(self, b"minimumHeight")
        )
        self.toggle_animation.addAnimation(
            QPropertyAnimation(self, b"maximumHeight")
        )
        self.clicked.connect(self.on_clicked)

    @pyqtSlot(name="clicked")
    def on_clicked(self):
        checked = self.isChecked()
        self.toggle_animation.setDirection(
            QAbstractAnimation.Backward
            if not checked
            else QAbstractAnimation.Forward
        )
        self.toggle_animation.start()

    def set_content_layout(self):
        collapsed_height = 20
        content_height = self.sizeHint().height()
        for i in range(self.toggle_animation.animationCount()):
            animation = self.toggle_animation.animationAt(i)
            animation.setDuration(300)
            animation.setStartValue(collapsed_height)
            animation.setEndValue(collapsed_height + content_height)
