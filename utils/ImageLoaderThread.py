import os.path
import queue
from PyQt5.QtCore import pyqtSignal, QThread, QMutex, QWaitCondition
import numpy as np
from PIL import Image as Image
import tifffile
from . import EZRT


class ImageLoaderThread(QThread):
    image_loaded = pyqtSignal(tuple, name="image_loaded")
    last_image = pyqtSignal(name="last_image")

    def __init__(self, parent=None, image_queue: queue.Queue = None):
        super().__init__(parent=parent)
        self.mutex = QMutex()
        self.condition = QWaitCondition()
        self.image_queue = image_queue

    def run(self):
        self.wait_for_signal()
        while not self.isInterruptionRequested():
            while not self.image_queue.empty():
                filepath, params, slot = self.image_queue.get()
                fex = filepath.split('.')[-1]
                try:
                    if fex == 'txt':
                        with open(filepath, 'r') as f:
                            arr = np.array([[x for x in line.split()] for line in f], params.dtype)
                    elif fex == 'raw':
                        _, arr = EZRT.loadImage(filepath)
                    elif fex in ['jpg', 'jpeg', 'png']:
                        arr = Image.open(filepath)
                        arr = np.array(arr.convert('L'))
                    elif fex in ['tiff', 'tif']:
                        arr = tifffile.imread(filepath)
                        if len(arr.shape) == 1:
                            arr = None
                        elif len(arr.shape) > 2:
                            if arr.shape[2] > 3:
                                arr = arr[:, :, :3]
                            arr = np.dot(arr, [0.299, 0.587, 0.114])
                    else:
                        offset = (os.path.getsize(filepath) -
                                  (params.width*params.height*np.dtype(params.dtype).itemsize))
                        arr = np.memmap(filepath, mode='r', dtype=params.dtype, shape=(params.width, params.height),
                                        offset=offset)
                        arr = np.array(arr)
                except Exception as e:
                    arr = None
                    filepath = e
                self.image_loaded.emit((arr, filepath, slot))
                if self.image_queue.empty():
                    self.last_image.emit()
            self.wait_for_signal()

    def wait_for_signal(self):
        self.mutex.lock()
        self.condition.wait(self.mutex)
        self.mutex.unlock()

    def wake(self):
        self.mutex.lock()
        self.condition.wakeAll()
        self.mutex.unlock()
