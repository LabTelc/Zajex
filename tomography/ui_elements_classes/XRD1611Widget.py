from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.uic import loadUiType

from tomography.flat_panel import FunctionCode, ErrorCode, Gain_NOP_Series, BinningMode
from ui_elements import icon_load, icon_add
from utils import LogTypes
import numpy as np

UI_XRD1611Widget, QWidget = loadUiType('./tomography/ui_elements/XRD1611.ui')


class XRD1611Widget(QWidget, UI_XRD1611Widget):
    new_image = pyqtSignal(tuple, name='new_image')

    def __init__(self, parent=None, queue=None):
        super().__init__(parent)
        self.setupUi(self)
        self.queue = queue
        self.image_buffer = np.zeros((4096,4096), np.uint32)
        self.last_image = None
        self.image_number = 0
        self.sequence_number = 0
        self.ob_image = None
        self.df_image = None
        self.bpm_image = None
        for corr in ["ob", "df", "bpm"]:
            getattr(self, f"tb_{corr}_file").setIcon(QIcon(icon_load))
            getattr(self, f"tb_{corr}_img").setIcon(QIcon(icon_add))
        self.cb_capacity.currentTextChanged.connect(self._cb_capacity_handler)
        self.rb_sum.clicked.connect(self._binning_handler)
        self.rb_avg.clicked.connect(self._binning_handler)
        self.cb_binning.currentTextChanged.connect(self._binning_handler)
        self.sb_exp_time.valueChanged.connect(self._exp_time_handler)
        self.pb_acquire.clicked.connect(self._acquire_handler)
        self.pb_abort.clicked.connect(self._abort_handler)
        self.pb_save.clicked.connect(self._save_handler)

    def new_image_acquired(self, arr, filepath):
        self.last_image = arr
        if self.gb_preview.isChecked():
            if self.cb_rotation.currentIndex() != 0:
                arr = np.rot90(arr, 4 - self.cb_rotation.currentIndex())
            if self.cb_mirrorLR.isChecked():
                arr = np.fliplr(arr)
            if self.cb_mirrorUD.isChecked():
                arr = np.flipud(arr)
            self.new_image.emit((arr, filepath, self.cb_slot.currentText().lower()))

    def new_message(self, func_code, status_code, payload):
        if status_code == ErrorCode.OK:
            self.log(FunctionCode.name(func_code))
            if func_code == FunctionCode.end_frame_callback:
                self.image_buffer += payload
                self.sequence_number += 1
            elif func_code == FunctionCode.end_acq_callback:
                self.new_image_acquired(np.uint16(self.image_buffer / self.sequence_number),
                                        f"XRD1611/Sequence_{self.sequence_number:04d}")
                self.sequence_number = 0
                self.image_number += 1
        else:
            self.log(f"Error in function {FunctionCode.name(func_code)}: {ErrorCode.name(status_code)}", LogTypes.Error)

    def log(self, text, log_type=LogTypes.Log):
        if log_type == LogTypes.Log:
            text = f"<font color='green'>{text}</font>"
        elif log_type == LogTypes.Warning:
            text = f"<font color='yellow'>Warning: {text}</font>"
        elif log_type == LogTypes.Error:
            text = f"<font color='red'>{text}</font>"
        self.log_widget.append(text)

    def _cb_capacity_handler(self):
        cap_code = "p".join(self.cb_capacity.currentText().split("."))
        self.queue.put((FunctionCode.set_camera_gain, (getattr(Gain_NOP_Series, f"g_{cap_code}"),)))

    def _binning_handler(self):
        flag_1 = "B_SUM" if self.rb_sum.isChecked() else "B_AVG"
        flag_2 = f"B_{self.cb_binning.currentText()}"
        self.queue.put(
            (FunctionCode.set_camera_binning_mode, (getattr(BinningMode, flag_1) | getattr(BinningMode, flag_2),)))

    def _exp_time_handler(self, value):
        self.queue.put((FunctionCode.set_timer_sync, (1000*value,)))

    def _acquire_handler(self):
        if self.cb_exp_mode.currentText() == "Frames":
            for i in range(self.sb_num_frames.value()):
                self.queue.put((FunctionCode.acquire_image, (1,)))
        elif self.cb_exp_mode.currentText() == "Integral":
            self.queue.put((FunctionCode.acquire_image, (self.sb_num_frames.value(),)))
        else:
            print("What?")

    def _abort_handler(self):
        self.queue.put((FunctionCode.abort, (None, )))

    def _save_handler(self):
        self.window().main_window.save_image(self.last_image, "bin", {"dtype":"uint16"})
