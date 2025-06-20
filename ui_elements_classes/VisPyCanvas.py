import os
import sys
from itertools import cycle
import tifffile

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QVBoxLayout

from vispy import scene
from vispy.scene import SceneCanvas
from vispy.color import get_colormaps, BaseColormap
from vispy.visuals.transforms import STTransform

CANVAS_SIZE = (600, 600)


class VisPyCanvas(QWidget):
    def __init__(self, parent=None):
        super(VisPyCanvas, self).__init__(parent)
        self.canvas = SceneCanvas(size=CANVAS_SIZE, keys=None)
        # add keys for action mapping

        self.view = self.canvas.central_widget.add_view()
        self.data = None
        self.volume = None
        self.fov = 60

        # self.cam_fly = scene.cameras.FlyCamera(parent=self.view.scene, fov=self.fov, name="FlyCamera")
        self.cam_tt = scene.cameras.TurntableCamera(parent=self.view.scene, fov=self.fov, name="TurntableCamera")
        self.cam_ab = scene.cameras.ArcballCamera(parent=self.view.scene, fov=self.fov, name="ArcballCamera")
        self.view.camera = self.cam_ab

    def set_data(self, data):
        self.data = data
        self.volume = scene.visuals.Volume(self.data, parent=self.view.scene)
        self.view.camera.center = np.array(self.data.shape) // 2
        self.canvas.update()


class TransFire(BaseColormap):
    glsl_map = """
    vec4 translucent_fire(float t) {
        return vec4(pow(t, 0.5), t, t*t, max(0, t*1.05 - 0.05));
    }
    """


class TransGrays(BaseColormap):
    glsl_map = """
    vec4 translucent_grays(float t) {
        return vec4(t, t, t, t*0.05);
    }
    """


if __name__ == '__main__':
    class MainWindow(QMainWindow):
        def __init__(self, data):
            super().__init__()
            self.setWindowTitle("3D Voxel Visualization")
            self.resize(800, 600)

            central_widget = QWidget(self)
            self.setCentralWidget(central_widget)

            layout = QVBoxLayout(central_widget)
            self.opengl_widget = VisPyCanvas(parent=central_widget)
            self.opengl_widget.set_data(data)
            layout.addWidget(self.opengl_widget.canvas.native)


    files = os.listdir("../data/Srsen3D")
    f = tifffile.imread(f"../data/Srsen3D/{files[0]}")
    arr = np.zeros((len(files), f.shape[0], f.shape[1]), dtype=f.dtype)
    for i, file in enumerate(files):
        slc = tifffile.imread(f"../data/Srsen3D/{file}")
        arr[i, :, :] = slc
        print("Working on file: ", file, end="\r")

    app = QApplication(sys.argv)
    window = MainWindow(arr)
    window.show()
    sys.exit(app.exec_())
