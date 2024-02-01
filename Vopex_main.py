# -*- coding: utf-8 -*-
"""
Created on 29.01.2024

@author: Zajicek
@author: Vopalensky
"""

from dataclasses import dataclass
import sys

from PyQt5.uic import loadUiType
from PyQt5.QtWidgets import QApplication

from ui_elements_classes.Palletes import *

supportedLoadFormats = ['raw', 'bin', 'txt']
supportedSaveFormats = ['raw', 'bin', 'txt', 'tif', 'jpg']
supportedDataTypes = ['int8', 'int16', 'int32', 'int64',
                      'uint8', 'uint16', 'uint32', 'uint64',
                      'float8', 'float16', 'float32', 'float64']

limits_dict = {0: "min - max", 1: "1 - 99", 2: "5 - 95", 3: "(min+1) - (max-1)"}
cmaps_list = ['gray', 'viridis', 'plasma', 'inferno', 'magma', 'cividis', 'Greys', 'Purples', 'Blues', 'Greens',
              'Oranges', 'Reds', 'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu', 'GnBu', 'PuBu', 'YlGnBu',
              'PuBuGn', 'BuGn', 'YlGn', 'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink', 'spring', 'summer',
              'autumn', 'winter', 'cool', 'Wistia', 'hot', 'afmhot', 'gist_heat', 'copper', 'PiYG', 'PRGn', 'BrBG',
              'PuOr', 'RdGy', 'RdBu', 'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic']

Ui_MainWindow, QMainWindow = loadUiType('./ui_elements/MainWindow2.ui')


@dataclass
class Parameters:
    ftype: str = 'bin'
    dtype: str = 'uint16'
    width: int = 4096
    height: int = 4096
    lower: float = 0
    upper: float = 65535
    x_lim: tuple = (0, width)
    y_lim: tuple = (height, 0)
    rotate: int = 0
    mirror_UD: bool = False
    mirror_LR: bool = False
    cmap: str = 'gray'
    from_zoom: bool = False


class Main(QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        super(Main, self).__init__()
        self.setupUi(self)
        self.palettes = {'dark': DarkPalette(), 'light': LightPalette()}
        self.parameters = Parameters()
        self.palette = 'dark'

        app.setPalette(self.palettes['dark'])

        input_handling_functions = self._input_handling_functions()
        for signal in input_handling_functions.keys():
            signal.connect(input_handling_functions[signal])

        self._init_gui_values()

    def _init_gui_values(self):
        for cmap in cmaps_list:
            self.cb_colormaps.addItem(cmap)

        for f in supportedSaveFormats:
            self.cb_save_a.addItem(f"Save all in A [{f}]")
            self.cb_save_b.addItem(f"Save all in B [{f}]")
            self.cb_save_c.addItem(f"Save all in C [{f}]")

        for r in limits_dict.values():
            self.cb_auto_range.addItem(r)

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
            self.cb_images_r.currentIndexChanged: self._cb_images_handler,
            self.le_operation.returnPressed: self._le_operation_handler,
            self.pb_save_all_calculated.clicked: self._pb_save_all_handler,
            self.slider_d.valueChanged: self._slider_handler,
        }

    def _cb_colormaps_handler(self, event):
        print(event)
        self.parameters.cmap = self.cb_colormaps.currentText()
        self._update()

    def _slider_limits_handler(self, event):
        print(event)

    def _dsb_limits_handler(self, event):
        print(event)
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
        print(event)

    def _pb_load_handler(self, event):
        print(event)

    def _cb_save_handler(self, event):
        print(event)

    def _slider_handler(self, event):
        print(event)

    def _le_operation_handler(self, event):
        print(event)

    def _update(self):
        print("Update")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    main = Main()

    main.show()
    app.exec_()
