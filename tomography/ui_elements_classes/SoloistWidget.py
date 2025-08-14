from PyQt5.QtGui import QIcon
from PyQt5.uic import loadUiType

from tomography.soloist import FunctionCode, AxisStatus
from tomography.ui_elements.icons import *
from utils import LogTypes

UI_SoloistWidget, QWidget = loadUiType('./tomography/ui_elements/Soloist.ui')

class SoloistWidget(QWidget, UI_SoloistWidget):
    def __init__(self, parent=None, queue=None):
        super().__init__(parent)
        self.setupUi(self)
        self.tb_state.setIcon(QIcon(icon_enable))
        self.tb_home.setIcon(QIcon(icon_home))
        self.tb_ack_all.setIcon(QIcon(icon_acknowledge))
        self.tb_abort.setIcon(QIcon(icon_abort))
        self.tb_reset.setIcon(QIcon(icon_reset))
        self.tb_move_ccw.setIcon(QIcon(icon_left))
        self.tb_move_cw.setIcon(QIcon(icon_right))
        self.queue = queue
        self.status = 0

        self.tb_state.clicked.connect(self._state_handler)
        self.tb_home.clicked.connect(lambda: self.post_message(FunctionCode.home))
        self.tb_ack_all.clicked.connect(lambda: self.post_message(FunctionCode.acknowledge_all))
        self.tb_abort.clicked.connect(lambda: self.post_message(FunctionCode.abort))
        self.tb_reset.clicked.connect(lambda:self.post_message(FunctionCode.reset))
        self.tb_move_ccw.clicked.connect(self.move)
        self.tb_move_cw.clicked.connect(self.move)

    def post_message(self, func_code, data=(None, )):
        self.queue.put((func_code, data))

    def new_message(self, func_code, status_code, payload):
        if status_code == 1:
            if func_code == FunctionCode.get_program_position_feedback:
                self.dsb_pos.setValue(payload)
            elif func_code == FunctionCode.get_axis_status:
                statuses = AxisStatus.get(payload)
                if "Homed" in statuses:
                    self.status = 1
                    self.tb_state.setIcon(QIcon(icon_disable))
                    self.le_axis_status.setText("Homed")
                    self.le_axis_status.setStyleSheet("QLineEdit { background-color: green; }")
                elif "Enabled" in statuses:
                    self.status = 1
                    self.tb_state.setIcon(QIcon(icon_disable))
                    self.le_axis_status.setText("Enabled")
                    self.le_axis_status.setStyleSheet("QLineEdit { background-color: green; }")
                else:
                    self.status = 0
                    self.le_axis_status.setText("Disabled")
                    self.le_axis_status.setStyleSheet("QLineEdit { background-color: gray; }")
            else:
                self.window().log(f"{FunctionCode.name(func_code)}: {payload}", LogTypes.Log)
        else:
            self.window().log(f"{FunctionCode.name(func_code)}: {payload}", LogTypes.Error)

    def _state_handler(self):
        if self.status == 0:
            self.post_message(FunctionCode.disable)
        elif self.status == 1:
            self.post_message(FunctionCode.enable)
        else:
            pass

    def move(self):
        speed = self.sb_speed.value()
        dist = self.sb_dist.value()
        dist = -dist if "ccw" in self.sender().objectName() else dist
        self.post_message(FunctionCode.move, (dist, speed))
