
import imageio
from PIL import Image

from PySide.QtCore import Signal
from PySide.QtCore import QThread


class GenMp4(QThread):

    finish_signal = Signal()

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
        print("MP4 save done!")
        self.finish_signal.emit()
