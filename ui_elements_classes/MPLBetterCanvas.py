from PyQt5.QtWidgets import (QLabel, QVBoxLayout, QWidget, QMenu, QFileDialog, )
from PyQt5.QtCore import pyqtSignal, Qt

from matplotlib import pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.widgets import RectangleSelector

from utils.ImageLoaderThread import ImageLoaderThread

import numpy as np
import os

list_item = 'application/x-qabstractitemmodeldatalist'


class MPLBetterCanvas(QWidget):
    image_updated = pyqtSignal(str, name='image updated')
    prev_ = pyqtSignal(name='prev')
    next_ = pyqtSignal(name='next')

    def __init__(self, parent=None):
        super().__init__(parent)
        # MPL Canvas
        self.fig = plt.figure()
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.canvas = FigureCanvas(self.fig)
        self.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.canvas.mpl_connect("motion_notify_event", self.on_mouse_move)
        self.canvas.mpl_connect('button_press_event', self.on_double_click)
        self.rect_selector = None
        # PyQt
        self.label = QLabel()
        self.label.setMaximumHeight(20)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label, 0, Qt.AlignRight)
        layout.addWidget(self.canvas, alignment=Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)
        self.setAcceptDrops(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.canvas_menu)
        # Image showing
        self.params = None
        self.image_path = None
        self.image_array = None
        self.cbar = None
        self.xlim = 0, 0
        self.ylim = 0, 0
        self.colorbar = None
        self.loader = ImageLoaderThread()
        self.loader.image_loaded.connect(self.image_loaded)
        self.loader.start()

    def _imshow(self):
        if self.image_array is None:
            return
        self.settings.update_limits()
        self.fig.delaxes(self.ax)
        if self.colorbar is not None:
            self.cax.clear()
            self.cax.axis('off')
            self.colorbar = None
        arr = self.image_array
        if not self.colorbar and not self.settings.show_axis:
            self.ax = self.fig.add_axes([0, 0, 1, 1])
        elif self.colorbar and not self.settings.show_axis:
            self.ax = self.fig.add_axes([0, 0, 1, 0.9])
        elif not self.colorbar and self.settings.show_axis:
            self.ax = self.fig.add_axes([0, 0.1, 0.95, 0.9])
        elif self.colorbar and self.settings.show_axis:
            self.ax = self.fig.add_axes([0, 0.1, 0.95, 0.8])
        self.im = self.ax.imshow(arr, cmap=self.settings.cmap, vmin=self.settings.vmin, vmax=self.settings.vmax)

        self.ax.get_xaxis().set_visible(self.settings.show_axis)
        self.ax.get_yaxis().set_visible(self.settings.show_axis)
        self.ax.set_xlim(self.xlim)
        self.ax.set_ylim(self.ylim)
        if self.settings.colorbar:
            self.cax = self.fig.add_axes([0.9, 0.05, 0.01, 0.8])
            self.cax.axis('on')
            self.cax.set_frame_on(False)
            self.colorbar = self.fig.colorbar(self.im, cax=self.cax, ax=self.ax)
        self.rect_selector = RectangleSelector(self.ax, self.on_select, useblit=True, button=[1], minspanx=5,
                                               minspany=5)
        self.ax.set_frame_on(False)
        self.canvas.draw()
        self.image_updated.emit("Image updated")

    def image_loaded(self, im):
        if not isinstance(im, np.ndarray) or self.image_path is None:
            return
        self.params = self.window().params
        self.parent().setTitle(f"Projection preview: {self.image_path.split('/')[-1]}")
        self.image_array = im
        self.settings.custom = False
        self.xlim = 0, self.image_array.shape[0]
        self.ylim = self.image_array.shape[1], 0
        self._imshow()

    def dragMoveEvent(self, event):
        data = event.mimeData()
        if data.hasFormat(list_item):
            event.acceptProposedAction()

    def dragEnterEvent(self, event):
        data = event.mimeData()
        if data.hasFormat(list_item):
            event.acceptProposedAction()

    def dropEvent(self, event):
        data = event.mimeData()
        if data.hasFormat(list_item):
            data = data.data(list_item)
            data = data.replace(b"\x00", b"")
            a = data.indexOf(b'\xca')
            b = data.indexOf(b'\n', a)
            filepath = str(data[(a + 1):b], 'utf-8')
            if os.path.exists(filepath):
                self.image_path = filepath
                self.loader.set_params(self.window().params)
                self.loader.set_image_path(filepath)

    def on_mouse_move(self, event):
        if event.inaxes and self.image_array is not None:
            x, y = event.xdata, event.ydata

            if x >= self.window().params.shape[0] or y >= self.window().params.shape[1]:
                return
            try:
                value = self.image_array[int(y + .5)][int(x + .5)]
            except IndexError:
                value = 0
            self.label.setText(f"row:{y:.0f}, col:{x:.0f} value:{value:.2f}")
        else:
            self.label.setText("")

    def on_select(self, eclick, erelease):
        x_min, x_max = min(eclick.xdata, erelease.xdata), max(eclick.xdata, erelease.xdata)
        y_min, y_max = min(eclick.ydata, erelease.ydata), max(eclick.ydata, erelease.ydata)

        if abs(x_max - x_min) < 5 or abs(y_max - y_min) < 5:
            return
        self.xlim = x_min, x_max
        self.ylim = y_max, y_min
        self.ax.set_xlim(self.xlim)
        self.ax.set_ylim(self.ylim)
        self.canvas.draw()

    def on_double_click(self, event):
        if event.button == 1 and event.dblclick and self.image_array is not None:
            self.xlim = 0, self.image_array.shape[0]
            self.ylim = self.image_array.shape[1], 0
            self.ax.set_xlim(self.xlim)
            self.ax.set_ylim(self.ylim)
            self.canvas.draw()

    def canvas_menu(self, pos):
        menu = QMenu()

        save_option = menu.addAction('Save picture')
        save_option.triggered.connect(self.save_picture)

        menu.exec_(self.mapToGlobal(pos))

    def save_picture(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save picture", "", "PNG Files (*.png)", )
        if file_path != "":
            self.fig.savefig(file_path)

    def on_scroll(self, event):
        if event.inaxes and self.image_array is not None:
            if 'ctrl' in event.modifiers:
                center_x, center_y = int(event.xdata + .5), int(event.ydata + .5)
                factor = event.step * 1 / np.e
                x_lim_l = smaller(self.xlim[0] + (center_x - self.xlim[0]) * factor, 0)
                x_lim_r = bigger(self.xlim[1] - (self.xlim[1] - center_x) * factor, self.image_array.shape[0])
                y_lim_l = bigger(self.ylim[0] - (self.ylim[0] - center_y) * factor, self.image_array.shape[0])
                y_lim_r = smaller(self.ylim[1] + (center_y - self.ylim[1]) * factor, 0)
                if x_lim_r - x_lim_l < 5 or y_lim_l - y_lim_r < 5:
                    return
                self.xlim = x_lim_l, x_lim_r
                self.ylim = y_lim_l, y_lim_r
                self.ax.set_xlim(self.xlim)
                self.ax.set_ylim(self.ylim)
                self.canvas.draw()
            else:
                if event.step > 0:
                    self.next_.emit()
                else:
                    self.prev_.emit()


def smaller(number, const):
    if number < const:
        return const
    return number


def bigger(number, const):
    if number > const:
        return const
    return number
