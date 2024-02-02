# -*- coding: utf-8 -*-
"""
Created on 29.01.2024

@author: Zajicek
@author: Vopalensky
"""
import os
import sys
from argparse import ArgumentParser
from dataclasses import dataclass
from queue import Queue

from PyQt5.QtWidgets import QApplication, QFileDialog, QDialog
from PyQt5.uic import loadUiType

from ui_elements_classes.CustomStandardItem import CustomStandardItem
from ui_elements_classes.FileInfoDialog import FileInfoDialog
from ui_elements_classes.Palletes import *
from utils.global_vars import *
from utils.utils import validate_input
from utils.ImageLoaderThread import ImageLoaderThread

Ui_MainWindow, QMainWindow = loadUiType('./ui_elements/MainWindow.ui')


@dataclass
class Parameters:
    dtype: str = 'uint16'
    header: int = 0
    width: int = 0
    height: int = 0
    lower: float = 0
    upper: float = 0
    x_lim: tuple = (0, width)
    y_lim: tuple = (height, 0)
    rotate: int = 0
    mirror_UD: bool = False
    mirror_LR: bool = False
    cmap: str = 'gray'
    from_zoom: bool = False
    last_dir: str = "./"


class Main(QMainWindow, Ui_MainWindow):
    def __init__(self, args):
        super(Main, self).__init__()
        self.setupUi(self)
        self.palettes = {'dark': DarkPalette(), 'light': LightPalette()}
        self.parameters = Parameters()
        if args.shape is not None:
            self.parameters.width, self.parameters.height = args.shape
        self.palette = 'dark'

        app.setPalette(self.palettes['dark'], )

        input_handling_functions = self._input_handling_functions()
        for signal in input_handling_functions.keys():
            signal.connect(input_handling_functions[signal])

        self.combo_boxes = {
            "a": self.cb_images_a,
            "b": self.cb_images_b,
            "c": self.cb_images_c,
            "d": self.cb_images_d,
        }
        self.images = {}
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
        self.loader = ImageLoaderThread(self)
        self.image_queue = Queue()
        self.id_gen = self.id_generator()

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
        }

    def _cb_colormaps_handler(self, event):
        print(event)
        self.parameters.cmap = self.cb_colormaps.currentText()
        self._update()

    def _slider_limits_handler(self, event):
        slider = self.sender().objectName().split('_')[-1]
        self.spin_boxes[slider].blockSignals(True)
        self.spin_boxes[slider].setValue(event)
        self.spin_boxes[slider].blockSignals(False)
        self._update()

    def _dsb_limits_handler(self, event):
        spin_box = self.sender().objectName().split('_')[-1]
        self.sliders[spin_box].blockSignals(True)
        self.sliders[spin_box].setValue(int(event))
        self.sliders[spin_box].blockSignals(False)
        self._update()

    def _cb_auto_range_handler(self, event):
        print(event)
        self._update()

    def _cb_from_zoom_handler(self):
        self.parameters.from_zoom = self.cb_from_zoom.isChecked()
        self._update()

    def _pb_apply_all_range_handler(self, event):
        print(event)

    def _sb_rows_handler(self):
        if self.sb_rows_to.value() > self.parameters.height:
            self.sb_rows_to.setValue(self.parameters.height)
        self.parameters.y_lim = (self.sb_rows_from.value(), self.sb_rows_to.value())
        self._update()

    def _sb_columns_handler(self):
        if self.sb_columns_to.value() > self.parameters.height:
            self.sb_columns_to.setValue(self.parameters.height)
        self.parameters.x_lim = (self.sb_columns_from.value(), self.sb_columns_to.value())
        self._update()

    def _un_zoom(self):
        self.parameters.x_lim = (0, self.parameters.width)
        self.parameters.y_lim = (self.height, 0)
        self._update()

    def _sb_apply_all_zoom_handler(self, event):
        print(event)

    def _pb_save_all_handler(self, event):
        print(event)

    def _cb_images_handler(self, event):
        group = self.sender().objectName().split('_')[-1]
        self.sliders[group].blockSignals(True)
        self.sliders[group].setValue(event)
        self.sliders[group].blockSignals(False)

    def _pb_load_handler(self):
        group = self.sender().objectName().split("_")[-1]
        combo_box = self.combo_boxes[group]

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
                self.image_queue.put(filepath)

        self.loader.wake()

    def _cb_save_handler(self, event):
        print(event)

    def _slider_handler(self, event):
        group = self.sender().objectName().split("_")[-1]
        self.combo_boxes[group].blockSignals(True)
        self.combo_boxes[group].setCurrentIndex(event)
        self.combo_boxes[group].blockSignals(False)

    def _le_operation_handler(self, event):
        print(event)

    def _image_loader_handler(self, event):
        arr, filepath, slot = event
        if arr is not None:
            im_id = next(self.id_gen)
            self.images[im_id] = arr
            item = CustomStandardItem(im_id)
            item.setName(filepath.split("/")[-1])
            item.setToolTip(filepath)
            self.combo_boxes[slot].add_custom_item(item)
            self.log(f"File {filepath} loaded.", LogTypes.Log)
        else:
            self.log(filepath, LogTypes.Error)

    def _update(self):
        print("Update")

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
