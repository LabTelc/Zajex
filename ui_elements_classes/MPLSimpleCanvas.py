from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt

from matplotlib import pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas


class MPLSimpleCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # MPL Canvas
        self.fig = plt.figure()
        self.canvas = FigureCanvas(self.fig)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.canvas, alignment=Qt.AlignCenter)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.setLayout(self.layout)

    def show_figure(self, figure: plt.Figure):
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)

        self.canvas = FigureCanvas(figure)
        self.layout.addWidget(self.canvas, alignment=Qt.AlignCenter)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.setLayout(self.layout)
