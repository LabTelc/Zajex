from PyQt5.QtCore import QThread, pyqtSignal
from socket import socket, AF_INET, SOCK_STREAM
from utils import get_config
config = get_config()["Server"]


class DetectorManagerThread(QThread):
    new_image = pyqtSignal(tuple, name="detector_message")
    new_message = pyqtSignal(tuple, name="detector_message")

    def __init__(self, parent=None):
        super().__init__(parent)
        self._socket = socket(AF_INET, SOCK_STREAM)
        self._socket.bind((config["host"], config["port"]))
        self._socket.listen(5)
        self._handlers = []
        self._queues = {}
        self.work_queue = None

    def handle_detector(self, worker_socket):
        while True:
            pass

    def run(self):
        raise NotImplementedError("This method should be implemented in a subclass.")

    def init_XRD1611(self):
        pass

    def init_XRD1622(self):
        pass

    def init_Dexela(self):
        pass