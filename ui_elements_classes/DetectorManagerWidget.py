from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QPlainTextEdit
from PyQt5.uic import loadUiType

UI_DetectorManagerWidget, QWidget = loadUiType('./ui_elements/QtUI/DetectorManagerWidget.ui')
UI_exposure, QGroupBox = loadUiType('./ui_elements/QtUI/exposure.ui')
UI_xrd_gain_binning, _ = loadUiType('./ui_elements/QtUI/xrd_gain_binning.ui')
UI_dexela_well_binning, _ = loadUiType('./ui_elements/QtUI/dexela_well_binning.ui')
UI_acquire, _ = loadUiType('./ui_elements/QtUI/acquire.ui')
UI_detector_corrections, _ = loadUiType('./ui_elements/QtUI/detector_corrections.ui')


class DetectorManagerWidget(QWidget, UI_DetectorManagerWidget):
    detector_tabs = {}

    def __init__(self, parent=None, dm=None, q=None):
        super(DetectorManagerWidget, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Detector Manager")
        self.result = None
        self.dm_thread = dm
        self.dm_queue = q
        if self.dm_thread.isRunning():
            self.l_manager.setText("Running")
            self.l_manager.setStyleSheet("color: green;")

    def _add_tab(self, name):
        dt = DetectorTab(self, name)
        self.detector_tabs[name] = dt
        self.tw_detectors.addTab(self.detector_tabs[name], name)
        dt.exp_mode_changed.connect(self.post_command)
        dt.seq_len_changed.connect(self.post_command)
        dt.exp_time_changed.connect(self.post_command)
        dt.start_acquisition.connect(self.post_command)
        dt.repeat_changed.connect(self.post_command)
        dt.gain_well_changed.connect(self.post_command)
        dt.binning_changed.connect(self.post_command)
        l_ = getattr(self, f"l_{name.lower()}")
        l_.setStyleSheet("color: green;")
        l_.setText("Running")

    def post_command(self, args):
        det, cmd, value = args
        self.dm_queue.put((det, (cmd, value)))
        self.dm_thread.wake()

    def detector_initialized(self, name):
        self._add_tab(name)


class Exposure(QGroupBox, UI_exposure):
    exp_mode_changed = pyqtSignal(str, name='exp_mode_changed')
    seq_len_changed = pyqtSignal(int, name='seq_len_changed')
    exp_time_changed = pyqtSignal(int, name='exp_time_changed')

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.cb_exp_mode.currentIndexChanged.connect(self.exp_mode)
        self.sb_num_frames.editingFinished.connect(self.seq_len)
        self.sb_exp_time.editingFinished.connect(self.exp_time)

    def seq_len(self):
        self.seq_len_changed.emit(self.sb_num_frames.value())

    def exp_time(self):
        self.exp_time_changed.emit(self.sb_exp_time.value())

    def exp_mode(self):
        self.exp_mode_changed.emit("F" if self.cb_exp_mode.currentText() == "Frames" else "I")


class Acquire(QWidget, UI_acquire):
    start_acquisition = pyqtSignal(int, name='start_acquisition')
    repeat_changed = pyqtSignal(bool, name='repeat_changed')

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.pb_acquisition.clicked.connect(lambda: self.start_acquisition.emit(None))
        self.cb_repeat.clicked.connect(self.repeat)

    def repeat(self):
        self.repeat_changed.emit(self.cb_repeat.isChecked())


class XRDGainBinning(QGroupBox, UI_xrd_gain_binning):
    gain_well_changed = pyqtSignal(str, name='gain_well_changed')
    binning_changed = pyqtSignal(tuple, name='binning_changed')

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.cb_capacity.currentIndexChanged.connect(self.gain_well)
        self.rb_avg.clicked.connect(self.binning)
        self.rb_accu.clicked.connect(self.binning)
        self.cb_binning.currentIndexChanged.connect(self.binning)

    def binning(self):
        self.binning_changed.emit(("avg" if self.rb_avg.isChecked() else "acc", self.cb_binning.currentText()))

    def gain_well(self):
        self.gain_well_changed.emit(self.cb_capacity.currentText())


class DexelaWellBinning(QGroupBox, UI_dexela_well_binning):
    gain_well_changed = pyqtSignal(str, name='gain_well_changed')
    binning_changed = pyqtSignal(tuple, name='binning_changed')

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.rb_x11.clicked.connect(self.binning)
        self.rb_x22.clicked.connect(self.binning)
        self.rb_x44.clicked.connect(self.binning)
        self.rb_high.clicked.connect(self.gain_well)
        self.rb_low.clicked.connect(self.gain_well)

    def binning(self):
        if self.rb_x22.isChecked():
            self.binning_changed.emit(("x22",))
        elif self.rb_x44.isChecked():
            self.binning_changed.emit(("x44",))
        else:
            self.binning_changed.emit(("x11",))

    def gain_well(self):
        self.gain_well_changed.emit("high" if self.rb_high.isChecked() else "low")


class WidePIXBinning(QWidget):
    gain_well_changed = pyqtSignal(str, name='gain_well_changed')
    binning_changed = pyqtSignal(tuple, name='binning_changed')

    def __init__(self, parent=None):
        super().__init__(parent)


class DetectorCorrections(QGroupBox, UI_detector_corrections):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)


class DetectorTab(QWidget):
    exp_mode_changed = pyqtSignal(tuple, name='exp_mode_changed')
    seq_len_changed = pyqtSignal(tuple, name='seq_len_changed')
    exp_time_changed = pyqtSignal(tuple, name='exp_time_changed')
    start_acquisition = pyqtSignal(tuple, name='start_acquisition')
    repeat_changed = pyqtSignal(tuple, name='repeat_changed')
    gain_well_changed = pyqtSignal(tuple, name='gain_well_changed')
    binning_changed = pyqtSignal(tuple, name='binning_changed')

    def __init__(self, parent=None, type_=""):
        super().__init__(parent)
        self.w_exposure = Exposure(self)
        self.w_corrections = DetectorCorrections(self)
        self.w_acquire = Acquire(self)
        if type_ == "Dexela":
            self.w_gb = DexelaWellBinning(self)
        elif type_ == "XRD1611" or type_ == "XRD1622":
            self.w_gb = XRDGainBinning(self)
        elif type_ == "WidePIX":
            self.w_gb = WidePIXBinning(self)
        else:
            self.w_gb = WidePIXBinning(self)
        self.pte_log = QPlainTextEdit(self)
        page_layout = QVBoxLayout()
        w1 = QWidget(self)
        l1 = QVBoxLayout()
        l1.addWidget(self.w_gb)
        l1.addWidget(self.w_exposure)
        w1.setLayout(l1)
        w2 = QWidget(self)
        l2 = QHBoxLayout()
        l2.addWidget(w1)
        l2.addWidget(self.w_corrections)
        w2.setLayout(l2)
        page_layout.addWidget(w2)
        page_layout.addWidget(self.w_acquire)
        page_layout.addWidget(self.pte_log)
        self.setLayout(page_layout)
        # Connecting elements
        self.w_exposure.exp_mode_changed.connect(lambda x: self.exp_mode_changed.emit((type_, "exp_mode", x)))
        self.w_exposure.seq_len_changed.connect(lambda x: self.seq_len_changed.emit((type_, "seq_len", x)))
        self.w_exposure.exp_time_changed.connect(lambda x: self.exp_time_changed.emit((type_, "exp_time", x)))
        self.w_acquire.start_acquisition.connect(lambda x: self.start_acquisition.emit((type_, "start_acq", x)))
        self.w_acquire.repeat_changed.connect(lambda x: self.repeat_changed.emit((type_, "repeat", x)))
        self.w_gb.gain_well_changed.connect(lambda x: self.gain_well_changed.emit((type_, "gain_well", x)))
        self.w_gb.binning_changed.connect(lambda x: self.binning_changed.emit((type_, "binning", x)))
