from PyQt5.QtWidgets import (QLabel, QVBoxLayout, QWidget, QMenu, QFileDialog, )
from PyQt5.QtCore import pyqtSignal, Qt

from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.widgets import RectangleSelector

import numpy as np

list_item = 'application/x-qabstractitemmodeldatalist'


class MPLBetterCanvas(QWidget):
    selection_changed = pyqtSignal(name='image updated')
    pixel_selected = pyqtSignal(float, name="pixel_selected")

    def __init__(self, parent=None):
        super().__init__(parent)
        # MPL Canvas
        self.fig = plt.figure(figsize=(20, 20))
        self.ax = self.fig.add_axes((0, 0, 1, 1))
        self.canvas = FigureCanvas(self.fig)
        self.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.canvas.mpl_connect("motion_notify_event", self.on_mouse_move)
        self.canvas.mpl_connect('button_press_event', self.on_left_click)
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
        # self.setAcceptDrops(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.canvas_menu)
        # Image showing
        self.params = None
        self.image = None
        self.cbar = None
        self.colorbar = None

    def _imshow(self):
        if self.image is None:
            return
        self.fig.delaxes(self.ax)
        if self.colorbar is not None:
            self.cax.clear()
            self.cax.axis('off')
            self.colorbar = None
        arr = self.image.array
        if not self.colorbar and not self.params.show_axis:
            self.ax = self.fig.add_axes((0, 0, 1, 1))
        elif self.colorbar and not self.params.show_axis:
            self.ax = self.fig.add_axes((0, 0, 1, 0.9))
        elif not self.colorbar and self.params.show_axis:
            self.ax = self.fig.add_axes((0, 0.1, 0.95, 0.9))
        elif self.colorbar and self.params.show_axis:
            self.ax = self.fig.add_axes((0, 0.1, 0.95, 0.8))
        self.im = self.ax.imshow(arr, cmap=self.params.cmap, vmin=self.image.vmin, vmax=self.image.vmax)

        self.ax.get_xaxis().set_visible(self.params.show_axis)
        self.ax.get_yaxis().set_visible(self.params.show_axis)
        self.ax.set_xlim(self.image.x_lim)
        self.ax.set_ylim(self.image.y_lim)
        if self.params.colorbar:
            self.cax = self.fig.add_axes((0.9, 0.05, 0.01, 0.8))
            self.cax.axis('on')
            self.cax.set_frame_on(False)
            self.colorbar = self.fig.colorbar(self.im, cax=self.cax, ax=self.ax)
        self.rect_selector = RectangleSelector(self.ax, self.on_select, useblit=True, button=[1], minspanx=5,
                                               minspany=5)
        self.ax.set_frame_on(False)
        self.canvas.draw()

    def show_image(self, image):
        self.image = image
        filename = image.filepath.split("/")[-1]
        self.params = self.window().parameters
        self.parent().setTitle(f"Image: {filename} [{image.array.shape[0]}x{image.array.shape[1]}]")
        self._imshow()

    def redraw(self):
        self.params = self.window().parameters
        self.image = self.window().curr_image
        self._imshow()

    # def dragMoveEvent(self, event, **kwargs):
    #     data = event.mimeData()
    #     if data.hasFormat(list_item):
    #         event.acceptProposedAction()
    #
    # def dragEnterEvent(self, event, **kwargs):
    #     data = event.mimeData()
    #     if data.hasFormat(list_item):
    #         event.acceptProposedAction()
    #
    # def dropEvent(self, event, **kwargs):
    #     data = event.mimeData()
    #     if data.hasFormat(list_item):
    #         data = data.data(list_item)
    #         data = data.replace(b"\x00", b"")
    #         a = data.indexOf(b'\xca')
    #         b = data.indexOf(b'\n', a)
    #         filepath = str(data[(a + 1):b], 'utf-8')

    def on_mouse_move(self, event):
        if event.inaxes and self.image is not None:
            x, y = event.xdata, event.ydata

            if x >= self.image.array.shape[1] or y >= self.image.array.shape[0]:
                return
            try:
                value = self.image.array[int(y + .5)][int(x + .5)]
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
        self.image.x_lim = int(x_min), int(x_max)
        self.image.y_lim = int(y_max), int(y_min)
        self.selection_changed.emit()

    def on_left_click(self, event):
        if event.button == 1 and self.image is not None:
            if event.dblclick:
                self.image.x_lim = 0, self.image.array.shape[1]
                self.image.y_lim = self.image.array.shape[0], 0
                self.selection_changed.emit()
            else:
                if event.inaxes:
                    x, y = event.xdata, event.ydata

                    if x >= self.image.array.shape[1] or y >= self.image.array.shape[1]:
                        return
                    try:
                        value = self.image.array[int(y + .5)][int(x + .5)]
                    except IndexError:
                        value = float("inf")
                    self.pixel_selected.emit(value)

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
        if event.inaxes and self.image is not None:
            if 'ctrl' in event.modifiers:
                center_x, center_y = int(event.xdata + .5), int(event.ydata + .5)
                factor = event.step * 1 / np.e
                x_lim_l = smaller(self.image.x_lim[0] + (center_x - self.image.x_lim[0]) * factor, 0)
                x_lim_r = bigger(self.image.x_lim[1] - (self.image.x_lim[1] - center_x) * factor,
                                 self.image.array.shape[0])
                y_lim_l = bigger(self.image.y_lim[0] - (self.image.y_lim[0] - center_y) * factor,
                                 self.image.array.shape[0])
                y_lim_r = smaller(self.image.y_lim[1] + (center_y - self.image.y_lim[1]) * factor, 0)
                if x_lim_r - x_lim_l < 5 or y_lim_l - y_lim_r < 5:
                    return
                self.image.x_lim = int(x_lim_l), int(x_lim_r)
                self.image.y_lim = int(y_lim_l), int(y_lim_r)
                self.selection_changed.emit()
            # else:
            #     if event.step > 0:
            #         self.next_.emit()
            #     else:
            #         self.prev_.emit()


def smaller(number, const):
    if number < const:
        return const
    return number


def bigger(number, const):
    if number > const:
        return const
    return number
