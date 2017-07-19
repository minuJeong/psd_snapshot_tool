
import numpy as np

import imageio
from PIL import Image

from PyQt5 import QtCore


class GenMp4(QtCore.QThread):

    finish_signal = QtCore.pyqtSignal()

    arrs = None
    target_dir = None
    target_framerate = None

    def __init__(self, arrs, target_dir, target_framerate):
        super(GenMp4, self).__init__()
        self.arrs = arrs
        self.target_dir = target_dir
        self.target_framerate = target_framerate

    def run(self):
        print("starting MP4 save..")
        imageio.mimwrite(f"{self.target_dir}/dst.mp4", self.arrs, fps=self.target_framerate)
        self.finish_signal.emit()
        print("MP4 save done!")
