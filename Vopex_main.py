# -*- coding: utf-8 -*-
"""
Created on 29.01.2024

@author: Zajicek
@author: Vopalensky
"""
import sys
from argparse import ArgumentParser
from queue import Queue

import numpy as np
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QFileDialog, QDialog
from PyQt5.uic import loadUiType

from ui_elements_classes.CustomStandardItem import CustomStandardItem
from ui_elements_classes.FileInfoDialog import FileInfoDialog
from ui_elements_classes.Palletes import *
from utils.global_vars import *
from utils.utils import validate_input
from utils.ImageLoaderThread import ImageLoaderThread

Ui_MainWindow, QMainWindow = loadUiType('./ui_elements/MainWindow.ui')
icon_path = './ui_elements/icon_64x.png'


@dataclass
class Parameters:
    dtype: str = 'uint16'
    header: int = 0
    width: int = 0
    height: int = 0
    vmin: float = 0
    vmax: float = 0
    x_lim: tuple = (0, width)
    y_lim: tuple = (height, 0)
    rotate: int = 0
    mirror_UD: bool = False
    mirror_LR: bool = False
    cmap: str = 'gray'
    from_zoom: bool = False
    last_dir: str = "./"
    colorbar: bool = False
    show_axis: bool = False


class Main(QMainWindow, Ui_MainWindow):
    def __init__(self, args):
        super(Main, self).__init__()
        self.setupUi(self)
        self.palettes = {'dark': DarkPalette(), 'light': LightPalette()}
        self.setWindowIcon(QIcon(icon_path))
        self.parameters = Parameters()

        if args.shape is not None:
            self.parameters.width, self.parameters.height = args.shape
        self.palette = 'dark'
        app.setPalette(self.palettes['dark'], None)

        self.image_queue = Queue()
        self.loader = ImageLoaderThread(self, image_queue=self.image_queue)
        self.loader.start()
        self.curr_id = None
        self.images = {}
        input_handling_functions = self._input_handling_functions()
        for signal in input_handling_functions.keys():
            signal.connect(input_handling_functions[signal])

        self.combo_boxes = {
            "a": self.cb_images_a,
            "b": self.cb_images_b,
            "c": self.cb_images_c,
            "d": self.cb_images_d,
        }
        self.sliders = {
            "a": self.slider_a,
            "b": self.slider_b,
            "c": self.slider_c,
            "d": self.slider_d,
            "lower": self.slider_lower,
            "upper": self.slider_upper
        }
        self.spin_boxes = {
            "lower": self.dsb_lower,
            "upper": self.dsb_upper,
            "rows_from": self.sb_rows_from,
            "rows_to": self.sb_rows_to,
            "columns_from": self.sb_columns_from,
            "columns_to": self.sb_columns_to,
        }
        self._init_gui_values()
        self.id_gen = self.id_generator()
        self.console_widget.get_locals()['images'] = self.images
        self.hist_ax = self.canvas_histogram.get_axis()

    def _init_gui_values(self):
        for cmap in cmaps_list:
            self.cb_colormaps.addItem(cmap)

        for f in supportedSaveFormats:
            self.cb_save_a.addItem(f"Save all in A [{f}]")
            self.cb_save_b.addItem(f"Save all in B [{f}]")
            self.cb_save_c.addItem(f"Save all in C [{f}]")

        for r in limits_dict.values():
            self.cb_auto_range.addItem(r)

        for s in self.sliders.values():
            s.setMaximum(0)

    def _input_handling_functions(self):
        return {
            # Figure settings
            # - Intensity values
            self.cb_colormaps.currentIndexChanged: self._cb_colormaps_handler,
            self.slider_lower.valueChanged: self._slider_limits_handler,
            self.slider_upper.valueChanged: self._slider_limits_handler,
            self.dsb_upper.valueChanged: self._dsb_limits_handler,
            self.dsb_lower.valueChanged: self._dsb_limits_handler,
            self.cb_auto_range.currentIndexChanged: self._cb_auto_range_handler,
            self.cb_from_zoom.stateChanged: self._cb_from_zoom_handler,
            self.pb_apply_all_range.clicked: self._pb_apply_all_range_handler,
            # - Zoomed Area
            self.sb_rows_from.valueChanged: self._sb_rows_handler,
            self.sb_rows_to.valueChanged: self._sb_rows_handler,
            self.sb_columns_from.valueChanged: self._sb_columns_handler,
            self.sb_columns_to.valueChanged: self._sb_columns_handler,
            self.pb_unzoom.clicked: self._un_zoom,
            self.pb_apply_all_zoom.clicked: self._sb_apply_all_zoom_handler,
            # -
            self.pb_save_all.clicked: self._pb_save_all_handler,

            # Assets
            # - A
            self.cb_images_a.currentIndexChanged: self._cb_images_handler,
            self.pb_load_a.clicked: self._pb_load_handler,
            self.cb_save_a.save_signal: self._cb_save_handler,
            self.slider_a.valueChanged: self._slider_handler,
            # - B
            self.cb_images_b.currentIndexChanged: self._cb_images_handler,
            self.pb_load_b.clicked: self._pb_load_handler,
            self.cb_save_b.save_signal: self._cb_save_handler,
            self.slider_b.valueChanged: self._slider_handler,
            # - C
            self.cb_images_c.currentIndexChanged: self._cb_images_handler,
            self.pb_load_c.clicked: self._pb_load_handler,
            self.cb_save_c.save_signal: self._cb_save_handler,
            self.slider_c.valueChanged: self._slider_handler,
            # - Operation
            self.cb_images_d.currentIndexChanged: self._cb_images_handler,
            self.le_operation.returnPressed: self._le_operation_handler,
            self.pb_save_all_calculated.clicked: self._pb_save_all_handler,
            self.slider_d.valueChanged: self._slider_handler,

            # Other
            self.loader.image_loaded: self._image_loader_handler,
            self.canvas_main.selection_changed: self._init_image_info_values
        }

    def _cb_colormaps_handler(self, event):
        print(event)
        self.parameters.cmap = self.cb_colormaps.currentText()
        self.canvas_main.redraw()

    def _slider_limits_handler(self, event):
        slider = self.sender().objectName().split('_')[-1]
        self.spin_boxes[slider].blockSignals(True)
        self.spin_boxes[slider].setValue(event)
        if slider == "upper":
            self.parameters.vmax = event
        elif slider == "lower":
            self.parameters.vmin = event
        self.spin_boxes[slider].blockSignals(False)
        self.canvas_main.redraw()

    def _dsb_limits_handler(self, event):
        spin_box = self.sender().objectName().split('_')[-1]
        self.sliders[spin_box].blockSignals(True)
        self.sliders[spin_box].setValue(int(event))
        self.sliders[spin_box].blockSignals(False)
        self.canvas_main.redraw()

    def _cb_auto_range_handler(self):
        if self.curr_id is None:
            return
        else:
            arr, _ = self.images[self.curr_id]
            idx = self.cb_auto_range.currentIndex()
            if idx == 0:
                self.parameters.vmin = arr.min()
                self.parameters.vmax = arr.max()
            elif idx == 1:
                self.parameters.vmin = np.percentile(arr, 1)
                self.parameters.vmax = np.percentile(arr, 99)
            elif idx == 2:
                self.parameters.vmin = np.percentile(arr, 5)
                self.parameters.vmax = np.percentile(arr, 95)
            elif idx == 3:
                self.parameters.vmin = arr.min() + 1
                self.parameters.vmax = arr.max() - 1
            self._init_image_info_values()

    def _cb_from_zoom_handler(self):
        self.parameters.from_zoom = self.cb_from_zoom.isChecked()
        self._init_image_info_values()

    def _pb_apply_all_range_handler(self, event):
        print(event)

    def _sb_rows_handler(self):
        if self.sb_rows_to.value() > self.parameters.height:
            self.sb_rows_to.setValue(self.parameters.height)
        self.parameters.y_lim = (self.sb_rows_from.value(), self.sb_rows_to.value())
        self._init_image_info_values()

    def _sb_columns_handler(self):
        if self.sb_columns_to.value() > self.parameters.height:
            self.sb_columns_to.setValue(self.parameters.height)
        self.parameters.x_lim = (self.sb_columns_from.value(), self.sb_columns_to.value())
        self._init_image_info_values()

    def _un_zoom(self):
        if self.curr_id is None:
            return
        arr, _ = self.images[self.curr_id]
        self.parameters.x_lim = 0, arr.shape[1]
        self.parameters.y_lim = arr.shape[0], 0
        self._init_image_info_values()

    def _sb_apply_all_zoom_handler(self, event):
        print(event)

    def _pb_save_all_handler(self, event):
        print(event)

    def _cb_images_handler(self, event):
        group = self.sender().objectName().split('_')[-1]
        self.sliders[group].blockSignals(True)
        self.sliders[group].setValue(event)
        im_id = self.combo_boxes[group].getCustomItem(event).im_id
        self._show_image(im_id)
        self.sliders[group].blockSignals(False)

    def _pb_load_handler(self):
        group = self.sender().objectName().split("_")[-1]

        filenames, filter_ = QFileDialog.getOpenFileNames(self, "Load images...",
                                                          self.parameters.last_dir, lFileTypeString,
                                                          initialFilter="All files (*.*)")
        if not filenames:
            return
        self.parameters.last_dir = filenames[0][:filenames[0].rfind("/")]

        for filepath in filenames:
            valid = False
            while not valid:
                valid = validate_input(filepath, self.parameters)
                if valid is None or valid:
                    break
                dialog = FileInfoDialog(self, self.parameters, ftype=filepath.split(".")[-1])
                if dialog.exec_() == QDialog.Accepted:
                    self.parameters.width = dialog.result["width"]
                    self.parameters.height = dialog.result["height"]
                    self.parameters.dtype = dialog.result["dtype"]
                else:
                    valid = None
                    break
            if valid is None:
                self.log(f"File {filepath} could not be loaded.", LogTypes.Error)
            else:
                self.image_queue.put((filepath, self.parameters, group))

        self.statusbar.start_progress(self.image_queue.qsize())
        self.loader.wake()

    def _cb_save_handler(self, event):
        print(event)

    def _slider_handler(self, event):
        group = self.sender().objectName().split("_")[-1]
        self.combo_boxes[group].blockSignals(True)
        self.combo_boxes[group].setCurrentIndex(event)
        im_id = self.combo_boxes[group].getCustomItem(event).im_id
        self._show_image(im_id)
        self.combo_boxes[group].blockSignals(False)

    def _le_operation_handler(self, event):
        print(event)

    def _image_loader_handler(self, event):
        arr, filepath, slot = event
        if arr is not None:
            self.sliders[slot].blockSignals(True)
            self.combo_boxes[slot].blockSignals(True)
            im_id = next(self.id_gen)
            self.images[im_id] = (arr, filepath)
            item = CustomStandardItem(im_id=im_id)
            item.setText(filepath.split("/")[-1])
            item.setToolTip(filepath)
            self.combo_boxes[slot].addCustomItem(item)
            self.log(f"File {filepath} loaded with ID: {im_id}.", LogTypes.Log)
            self.sliders[slot].setMaximum(self.combo_boxes[slot].count() - 1)
            self.statusbar.add_progress()
            self.sliders[slot].blockSignals(False)
            self.combo_boxes[slot].blockSignals(False)
        else:
            self.log(filepath, LogTypes.Error)

    def _init_image_info_values(self):
        if self.curr_id is None:
            return
        for sb in self.spin_boxes.values():
            sb.blockSignals(True)

        arr, filename = self.images[self.curr_id]
        self.spin_boxes['lower'].setRange(self.parameters.vmin, self.parameters.vmax)
        self.spin_boxes['upper'].setRange(self.parameters.vmin, self.parameters.vmax)
        self.sliders['lower'].setMaximum(100)
        self.sliders['upper'].setMaximum(100)
        self.spin_boxes['rows_from'].setValue(self.parameters.x_lim[0])
        self.spin_boxes['rows_to'].setValue(self.parameters.x_lim[1])
        self.spin_boxes['columns_from'].setValue(self.parameters.y_lim[1])
        self.spin_boxes['columns_to'].setValue(self.parameters.y_lim[0])
        self.l_im_mean.setText(str(arr.mean()))
        self.l_im_sigma.setText(str(arr.std()))
        self.l_range_mean.setText(str(arr[self.parameters.x_lim[0]:self.parameters.x_lim[1],
                                      self.parameters.y_lim[1]:self.parameters.y_lim[0]].mean()))
        self.l_range_sigma.setText(str(arr[self.parameters.x_lim[0]:self.parameters.x_lim[1],
                                       self.parameters.y_lim[1]:self.parameters.y_lim[0]].std()))

        for sb in self.spin_boxes.values():
            sb.blockSignals(False)

    def _show_image(self, im_id):
        self.curr_id = im_id
        arr, filepath = self.images[im_id]
        self.parameters.vmin = arr.min()
        self.parameters.vmax = arr.max()
        self.parameters.x_lim = (0, arr.shape[0])
        self.parameters.y_lim = (arr.shape[1], 0)
        self.canvas_main.show_image(arr, filepath.split("/")[-1], im_id)
        self.hist_ax.hist(self.images[im_id][0].flatten())
        self.canvas_histogram.redraw()
        self._init_image_info_values()

    def log(self, text, log_type=LogTypes.Log):
        if log_type == LogTypes.Log:
            text = f"{text}"
        elif log_type == LogTypes.Warning:
            text = f"<font color='yellow'>Warning: {text}</font>"
        elif log_type == LogTypes.Error:
            text = f"<font color='red'>{text}</font>"
        self.log_widget.append(text)

    @staticmethod
    def id_generator():
        current_id = 0
        while True:
            yield current_id
            current_id += 1

    def closeEvent(self, event):
        self.loader.requestInterruption()
        self.loader.wake()
        event.accept()
        app.exit(0)


if __name__ == '__main__':
    parser = ArgumentParser(
        prog="Vopex 3.0",
        description='',
        epilog="")
    parser.add_argument("-s", "--shape", nargs=2, type=int, metavar=("width", "height"),
                        help="Shape of input images")
    cmd_args = parser.parse_args()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    main = Main(cmd_args)

    main.show()
    app.exec_()
