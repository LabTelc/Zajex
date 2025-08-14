import os
import queue

from PyQt5.QtCore import pyqtSignal, QThread, QMutex, QWaitCondition

from .utils import get_save_image


class ImageSaverThread(QThread):
    image_saved = pyqtSignal(str, name="image_saved")
    delete_signal = pyqtSignal(int, name="delete_signal")

    def __init__(self, parent=None, image_queue: queue.Queue = None, images=None):
        super().__init__(parent=parent)
        self.mutex = QMutex()
        self.condition = QWaitCondition()
        self.image_queue = image_queue
        self.images = images

    def run(self):
        self.wait_for_signal()
        while not self.isInterruptionRequested():
            while not self.image_queue.empty():
                im_id, ftype, file_path, kwargs = self.image_queue.get()
                if isinstance(im_id, int):
                    image = self.images[im_id]
                else:
                    image = im_id
                name = image.filepath.split("/")[-1].split(".")[:-1]
                name = "".join(name)
                while os.path.exists(os.path.join(file_path, name + "." + ftype)):
                    name = name + "(1)"
                get_save_image(ftype)(image.array, name, file_path, **kwargs)
                self.image_saved.emit(os.path.join(file_path, name + "." + ftype))
                if "remove" in kwargs.keys():
                    self.delete_signal.emit(im_id)
            self.wait_for_signal()

    def wait_for_signal(self):
        self.mutex.lock()
        self.condition.wait(self.mutex)
        self.mutex.unlock()

    def wake(self):
        self.mutex.lock()
        self.condition.wakeAll()
        self.mutex.unlock()
