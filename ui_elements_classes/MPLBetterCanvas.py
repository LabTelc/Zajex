import numpy as np
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QMenu, QFileDialog
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.widgets import RectangleSelector
from scipy.interpolate import RegularGridInterpolator
from scipy.spatial.distance import euclidean

distance_limit = 30


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
        self.canvas.mpl_connect('button_press_event', self.on_mouse_click)
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
        self.image = None
        self.cbar = None
        self.points = []
        self.plot_profile_window = None

    def _imshow(self):
        if self.image is None:
            return
        self.fig.delaxes(self.ax)
        self.ax = self.fig.add_axes((0, 0, 1, 1))
        arr = self.image.array
        self.im = self.ax.imshow(arr, cmap=self.params.cmap, vmin=self.image.vmin, vmax=self.image.vmax)

        self.ax.get_xaxis().set_visible(self.params.show_axes)
        self.ax.get_yaxis().set_visible(self.params.show_axes)
        self.ax.set_xlim(self.image.x_lim)
        self.ax.set_ylim(self.image.y_lim)
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

    def dragEnterEvent(self, event, **kwargs):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event, **kwargs):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event, **kwargs):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            file_paths = [url.toLocalFile() for url in urls]
            self.window().open_files(file_paths, "a")
            event.accept()
        else:
            event.ignore()

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

    def on_select(self, event_click, event_release):
        x_min, x_max = min(event_click.xdata, event_release.xdata), max(event_click.xdata, event_release.xdata)
        y_min, y_max = min(event_click.ydata, event_release.ydata), max(event_click.ydata, event_release.ydata)

        if abs(x_max - x_min) < 5 or abs(y_max - y_min) < 5:
            return
        self.image.x_lim = int(x_min), int(x_max)
        self.image.y_lim = int(y_max), int(y_min)
        self.points = []
        self.selection_changed.emit()

    def on_mouse_click(self, event):
        if self.image is None:
            return
        if event.button == 1:  # left click
            if event.dblclick:
                self.image.x_lim = 0, self.image.array.shape[1]
                self.image.y_lim = self.image.array.shape[0], 0
                self.selection_changed.emit()
                self.points = []
            else:
                if event.inaxes:
                    x, y = event.xdata, event.ydata

                    if x >= self.image.array.shape[1] or y >= self.image.array.shape[0]:
                        return
                    try:
                        value = self.image.array[int(y + .5)][int(x + .5)]
                    except IndexError:
                        value = float("inf")
                    if 'ctrl' in event.modifiers and "shift" not in event.modifiers:
                        self.add_point(x, y)
                    elif 'ctrl' in event.modifiers and "shift" in event.modifiers:
                        self.remove_point(x, y)
                    self.pixel_selected.emit(value)

    def add_point(self, x, y):
        if len(self.points) == 0:
            self.points.append((x, y))
            self.ax.scatter(x, y, c='r', marker='+')
        elif len(self.points) == 1:
            self.points.append((x, y))
            self.ax.scatter(x, y, c='r', marker='+')
            self.ax.plot((x, self.points[0][0]), (y, self.points[0][1]), linestyle="--", c="g")
            self.plot_profile(*self.points)
        elif len(self.points) == 2:
            self.redraw()
            self.points = [self.points[1], (x, y)]
            self.ax.scatter(x, y, c='r', marker='+')
            self.ax.scatter(*self.points[0], c='r', marker='+')
            self.ax.plot((x, self.points[0][0]), (y, self.points[0][1]), linestyle="--", c="g")
            self.plot_profile(*self.points)
        self.canvas.draw()

    def remove_point(self, x, y):
        if len(self.points) == 0:
            return
        elif len(self.points) == 1:
            if euclidean(np.array(self.points[0]), np.array([x, y])) < distance_limit:
                self.points = []
                self.redraw()
        else:
            d1 = euclidean(np.array(self.points[0]), np.array([x, y]))
            d2 = euclidean(np.array(self.points[1]), np.array([x, y]))
            if d1 < distance_limit < d2:
                p = self.points[1]
            elif d2 < distance_limit < d1:
                p = self.points[0]
            else:
                return
            self.points = []
            self.redraw()
            self.add_point(*p)

    def plot_profile(self, p0, p1):
        interp = RegularGridInterpolator(
            (np.arange(0, self.image.array.shape[0]), np.arange(0, self.image.array.shape[1])), self.image.array,
            "nearest")
        p0, p1 = (p0, p1) if p0[0] < p1[0] else (p1, p0)
        line_points = bresenham_line(p0, p1)
        data = interp(line_points)
        # data = np.array([interp((x, y)) for x, y in line_points])

        window = ProfileWindow(data)
        self.plot_profile_window = window
        window.show()

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
                self.points = []
                self.selection_changed.emit()

    def reset_canvas(self):
        self.ax.clear()
        self.canvas.draw()


class ProfileWindow(QWidget):
    def __init__(self, data=None):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Line profile")
        self.setMinimumSize(200, 100)
        new_canvas = MplCanvas(self, width=5, height=4, dpi=100)
        new_canvas.axes.plot(data)

        layout = QVBoxLayout()
        layout.addWidget(new_canvas)
        self.setLayout(layout)


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


def smaller(number, const):
    if number < const:
        return const
    return number


def bigger(number, const):
    if number > const:
        return const
    return number


def bresenham_line(p0, p1):
    y0, x0 = p0
    y1, x1 = p1
    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        points.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

    return points
