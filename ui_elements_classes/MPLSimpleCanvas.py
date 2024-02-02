from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt

from matplotlib import pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas


class MPLSimpleCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # MPL Canvas
        self.fig = plt.figure()
        self.ax = self.fig.add_axes((0, 0, 1, 1))
        self.canvas = FigureCanvas(self.fig)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.canvas, alignment=Qt.AlignCenter)
        # self.layout.setContentsMargins(0, 0, 0, 0)
        # self.layout.setSpacing(0)

        self.setLayout(self.layout)

    def get_axis(self):
        self.ax.clear()
        return self.ax

    def redraw(self):
        self.canvas.draw()
