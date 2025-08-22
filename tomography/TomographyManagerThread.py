from socket import socket, AF_INET, SOCK_STREAM
from queue import Queue
import subprocess
import select
from threading import Thread
import numpy as np

from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QWaitCondition

from utils import get_config
from tomography.Socket import recv_unpack_message, send_message
from tomography.flat_panel import FlatPanelEnums
from tomography.soloist import SoloistEnums

config = get_config()["Server"]
timeout = float(config["timeout"])
tables = config["tables"].split(" ")
detectors = config["detectors"].split(" ")
python_27 = config["python_27"]

class TomographyManagerThread(QThread):
    new_message = pyqtSignal(tuple, name="detector_message")
    worker_initialized = pyqtSignal(tuple, name="worker_initialized")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mutex = QMutex()
        self.condition = QWaitCondition()
        self._socket = socket(AF_INET, SOCK_STREAM)
        self._worker_processes = []
        self._worker_threads = []
        self._queues = {}

    def handle_worker(self, worker_socket):
        func_code, status_code, name = recv_unpack_message(worker_socket)
        if name in detectors:
            error_enum = FlatPanelEnums.ErrorCode
            success_code = 0
        elif name in tables:
            error_enum = SoloistEnums.ErrorCode
            success_code = 1
        else:
            self.new_message.emit(("TomographyManager", 0, f"Unknown worker: \"{name}\""))
            return

        if status_code == success_code:
            q = Queue()
            self._queues[name] = q
            self.worker_initialized.emit((name, q))
        else:
            self.new_message.emit(("TomographyManager", f"[{name}]: Not initialized: {error_enum.name(status_code)}"))
            return

        while not self.isInterruptionRequested():
            ready_to_read, _, _ = select.select([worker_socket], [], [], timeout)
            if ready_to_read:
                try:
                    self.new_message.emit((name, *recv_unpack_message(worker_socket)))
                except Exception as e:
                    self.new_message.emit((name, -1, -1, f"Error receiving data: {str(e)}"))
                    return

            while not self._queues[name].empty():
                try:
                    func, data = self._queues[name].get()
                    send_message(worker_socket, func, success_code, data)
                except Exception as e:
                    self.new_message.emit((name, -1, -1, f"Error sending data: {str(e)}"))
                    return

    def run(self):
        self._socket.bind((config["host"], int(config["port"])))
        self._socket.listen(5)
        self.new_message.emit(("TomographyManager", 0, f"Listening on {config['host']}:{config['port']}"))

        for detector in detectors:
            self.new_message.emit(("TomographyManager", 0, f"Starting {detector} detector"))
            with open(f"logs/{detector}.log", "w") as logfile:
                self._queues[detector.lower()] = Queue()
                w = subprocess.Popen(f"{python_27} tomography/{detector}.py", stdout=logfile, stderr=logfile,
                                     creationflags=subprocess.CREATE_NO_WINDOW)
                self._worker_processes.append(w)

        for table in tables:
            self.new_message.emit(("TomographyManager", 0, f"Starting {table} table"))
            with open(f"logs/{table}.log", "w") as logfile:
                self._queues[table.lower()] = Queue()
                w = subprocess.Popen(f"{python_27} tomography/{table}.py", stdout=logfile, stderr=logfile,
                                     creationflags=subprocess.CREATE_NO_WINDOW)
                self._worker_processes.append(w)

        for _ in range(len(self._worker_processes)):
            worker_socket, address = self._socket.accept()
            worker = Thread(target=self.handle_worker, args=(worker_socket,))
            worker.daemon = True
            self._worker_threads.append(worker)
            worker.start()
            self.new_message.emit(("TomographyManager", 0, f"Accepted connection from {address}"))

        self.wait_for_signal()
        for process in self._worker_processes:
            process.terminate()
            process.wait()

    def wait_for_signal(self):
        self.mutex.lock()
        self.condition.wait(self.mutex)
        self.mutex.unlock()

    def wake(self):
        self.mutex.lock()
        self.condition.wakeAll()
        self.mutex.unlock()