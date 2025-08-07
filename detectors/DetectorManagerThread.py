from socket import socket, AF_INET, SOCK_STREAM
from queue import Queue
import subprocess
import select
from threading import Thread
import numpy as np

from PyQt5.QtCore import QThread, pyqtSignal

from utils import get_config, LogTypes
from .Socket import *
from .FlatPanelEnums import ErrorCodes, FunctionCode

config = get_config()["Server"]
timeout = float(config["timeout"])


class DetectorManagerThread(QThread):
    new_image = pyqtSignal(tuple, name="detector_message")
    new_message = pyqtSignal(tuple, name="detector_image")  # (arr, filepath (info/name), slot)
    detector_initialized = pyqtSignal(str, name="detector_initialized")

    def __init__(self, parent=None):
        super().__init__(parent)
        self._socket = socket(AF_INET, SOCK_STREAM)
        self._handlers = []
        self._worker_processes = []
        self._worker_threads = []
        self._queues = {}

    def handle_detector(self, worker_socket):
        image_index = 0
        func_code, status_code, name = recv_unpack_message(worker_socket)
        if status_code == 0:
            self.new_message.emit((f"[{name}]: Initialized", LogTypes.Log))
            self._queues[name] = Queue()
        else:
            self.new_message.emit((f"[{name}]: Not initialized: {ErrorCodes.name(status_code)}", LogTypes.Error))
            return
        while not self.isInterruptionRequested():
            ready_to_read, _, _ = select.select([worker_socket], [], [], timeout)
            if ready_to_read:
                try:
                    func_code, status_code, message = recv_unpack_message(worker_socket)
                except Exception as e:
                    self.new_message.emit((f"[{name}]: Error receiving data: {str(e)}", LogTypes.Error))
                    break
                print(func_code)
                self.new_message.emit((f"[{name}]: {FunctionCode.name(func_code)}: {ErrorCodes.name(status_code)}", LogTypes.Error if status_code != 0 else LogTypes.Log))
                if isinstance(message, np.ndarray):
                    self.new_image.emit((message, f"{name}_{image_index:04d}", "a"))
            else:
                while not self._queues[name].empty():
                    try:
                        func, data = self._queues[name].get()
                        send_message(worker_socket, getattr(func_code, data[0]), 0, data[1])
                    except Exception as e:
                        self.new_message.emit((f"[{name}]: Error sending data: {str(e)}", LogTypes.Error))
                        return

    def run(self):
        self._socket.bind((config["host"], int(config["port"])))
        self._socket.listen(5)
        self.new_message.emit((f"[DetectorManager]: Listening on {config['host']}:{config['port']}", LogTypes.Log))

        detectors = config["detectors"]
        for detector in detectors.split(" "):
            with open(f"logs/{detector}.log", "a") as logfile:
                self._queues[detector.lower()] = Queue()
                w = subprocess.Popen(f"conda run -n py27 python detectors/{detector}.py",
                                     stdout=logfile, stderr=logfile, cwd="./")
                self._worker_processes.append(w)

        while not self.isInterruptionRequested():
            worker_socket, address = self._socket.accept()
            worker = Thread(target=self.handle_detector, args=(worker_socket,))
            self._worker_threads.append(worker)
            worker.start()
            self.new_message.emit((f"[DetectorManager]: Accepted connection from {address}", LogTypes.Log))

        for worker in self._worker_threads:
            worker.join()

        for process in self._worker_processes:
            process.terminate()
            process.wait()