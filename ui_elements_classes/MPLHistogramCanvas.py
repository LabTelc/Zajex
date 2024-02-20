from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

import matplotlib
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class MPLHistogramCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # MPL Canvas
        self.fig = plt.figure()
        self.ax = self.fig.add_axes((.01, .1, .98, .89))
        self.canvas = FigureCanvas(self.fig)
        self.canvas.mpl_connect("motion_notify_event", self.on_mouse_move)

        self.label = QLabel(self)
        layout = QVBoxLayout(self)
        layout.addWidget(self.label, 0, Qt.AlignRight)
        layout.addWidget(self.canvas, alignment=Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.setLayout(layout)

    def plot_histogram(self, image, parameters, value=None):
        self.ax.clear()
        data = image.array.flatten()
        counts, bins, patches = self.ax.hist(data, bins=parameters.num_bins, edgecolor='none', linewidth=1.2)
        self.ax.axvline(image.vmin, color='r')
        self.ax.axvline(image.vmax, color='r')

        bin_means = [(bins[i] + bins[i + 1]) / 2 for i in range(parameters.num_bins)]
        colormap = matplotlib.colormaps[parameters.cmap]
        norm_bin_means = (bin_means - image.vmin) / (image.vmax - image.vmin)

        # Assign colors to the patches based on the mean values
        for i, patch in enumerate(patches):
            color = colormap(norm_bin_means[i])
            patch.set_facecolor(color)

        arrow_value = parameters.ratio * (image.vmax - image.vmin) + image.vmin
        for i, bin_mean in enumerate(bin_means):
            if bins[i] <= arrow_value <= bins[i + 1]:
                self.ax.annotate("", xy=(bin_mean, max(counts)), xytext=(bin_mean, max(counts) + 10),
                                 arrowprops=dict(arrowstyle="->", connectionstyle="arc3", color="red",
                                                 lw=2))

            if value is not None:
                if bins[i] <= value <= bins[i + 1]:
                    patches[i].set_facecolor('green')

        self.ax.grid(True)
        self.canvas.draw()

    def on_mouse_move(self, event):
        if event.inaxes:
            self.label.setText(f"{event.xdata}")
        else:
            self.label.setText("")
