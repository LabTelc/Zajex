from PyQt5.QtCore import pyqtSignal, QThread, QMutex, QWaitCondition

import numpy as np


class ImageLoaderThread(QThread):
    image_loaded = pyqtSignal(np.ndarray, name="image_loaded")
    error_produced = pyqtSignal(str, name='Error')

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.mutex = QMutex()
        self.condition = QWaitCondition()
        self.params = None
        self.image_path = None

    def run(self):
        self.wait_for_signal()
        while not self.isInterruptionRequested():
            if self.image_path:
                try:
                    arr = np.memmap(self.image_path, dtype=self.params.dtype_in, mode='r', shape=self.params.shape)
                except OSError:
                    arr = None
                arr = np.array(arr)
                if arr is None:
                    self.image_path = None
                    self.error_produced.emit("Invalid file or input parameters")
                if self.params.mirror:
                    arr = np.flip(arr)
                arr = np.rot90(arr, k=-self.params.rotate)
                self.image_loaded.emit(arr)
                self.image_path = None
                self.wait_for_signal()

    def wait_for_signal(self):
        self.mutex.lock()
        self.condition.wait(self.mutex)
        self.mutex.unlock()

    def set_image_path(self, image_path):
        self.image_path = image_path
        self.mutex.lock()
        self.condition.wakeAll()
        self.mutex.unlock()

    def set_params(self, params):
        self.params = params
        self.mutex.lock()
        self.condition.wakeAll()
        self.mutex.unlock()
