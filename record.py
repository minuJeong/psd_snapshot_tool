
"""
dependency
 - PyQt5
 - win32com
 - Pillow
 - imagehash
 - psd_tools

"""

import os
import platform
import time
import datetime
import subprocess
from threading import Thread
from threading import Lock
from threading import active_count

import imagehash
import numpy as np
import imageio
from psd_tools import PSDImage
from PIL import Image

from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal
from PyQt5.Qt import Qt
from PyQt5.QtGui import QIntValidator

from win32com import client

from ui.record import mainwindow


class CONST(object):
    @property
    def DEFAULT_PATH(self):
        try:
            psapp = client.Dispatch("Photoshop.Application").Application
            doc = psapp.ActiveDocument
        except:
            return None
        return f"{doc.path}{doc.name}"


class PSDStoreThread(QThread):
    psd_path = None
    png_path = None
    override_size = None
    hashlock = None
    last_hash = None

    save_success_signal = pyqtSignal()

    def __init__(self, psd_path, png_path, override_size, hashlock, last_hash):
        super(PSDStoreThread, self).__init__()

        self.psd_path = psd_path
        self.png_path = png_path
        self.override_size = override_size
        self.hashlock = hashlock
        self.last_hash = last_hash

    def run(self):
        self.hashlock.acquire()

        # load first
        psd_img = PSDImage.load(self.psd_path)
        if not psd_img:
            print("[ERROR] Can't load psd image")

            # hard reset hash
            self.last_hash = [None]
            self.hashlock.release()
            return

        as_img = psd_img.as_PIL()
        hashcode = imagehash.average_hash(as_img, hash_size=32)
        if hashcode == self.last_hash[-1]:
            self.hashlock.release()
            return

        self.last_hash.append(hashcode)
        self.hashlock.release()

        # save image file
        org_size = as_img.size
        if self.override_size[0] != 0 and self.override_size[1] != 0:
            target_w = self.override_size[0]
            target_h = self.override_size[1]

            w_ratio = target_w / org_size[0]
            h_ratio = target_h / org_size[1]

            target_ratio = min(w_radef, h_ratio)
            target_w = int(org_sizedef * target_ratio)
            target_h = int(org_sizedef * target_ratio)

            target_size = (target_w, target_h)
        else:
            target_size = org_size

        as_img = as_img.resize(target_size)
        as_img.save(self.png_path)

        print("Snapshot!")
        self.save_success_signal.emit()


class PSDStoreThreadHolder(QThread):

    target_dirpath = None
    target_psd_path = None
    target_width = 0
    target_height = 0

    index = 0

    cancellation_token = pyqtSignal()
    finish_signal = pyqtSignal()

    cancellation_token_flipped = False

    def __init__(self, target_dirpath, target_psd_path, target_width, target_height):
        super(PSDStoreThreadHolder, self).__init__()
        self.target_dirpath = target_dirpath
        self.target_psd_path = target_psd_path
        self.target_width = target_width
        self.target_height = target_height

        self.cancellation_token.connect(self.cancel)

    def cancel(self, e=None):
        self.cancellation_token_flipped = True

    def run(self):
        hashlock = Lock()
        last_hash = [None]
        as_img = None

        while True:
            if self.cancellation_token_flipped:
                break

            time.sleep(0.75)

            last_hash = last_hash[-1:]
            psd_thread = PSDStoreThread(
                self.target_psd_path,
                self.get_cachename(),
                (self.target_width, self.target_height),
                hashlock,
                last_hash
            )

            psd_thread.save_success_signal.connect(self.add_index)
            psd_thread.start()
            psd_thread.wait()

        # will never happen
        self.finish_signal.emit()

    def add_index(self):
        self.index += 1

    def get_cachename(self):
        return f"{self.target_dirpath}/cached_{self.index}.png"


class WindowHandler(mainwindow.Ui_MainWindow):

    const = CONST()
    workthread = None

    def __init__(self, mainwin):
        super(WindowHandler, self).__init__()

        self.mainwin = mainwin
        self.mainwin.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.setupUi(self.mainwin)

        self.PSDPathLineInput.setText(self.const.DEFAULT_PATH)
        self.MakeDivisable16Button.clicked.connect(self.make_divisable_by_16)
        self.ShowDirectoryButton.clicked.connect(self.showdir)
        self.StartButton.clicked.connect(self.start)
        self.StopButton.clicked.connect(self.stop)

    def make_divisable_by_16(self, e):
        try:
            psapp = client.Dispatch("Photoshop.Application").Application
            if not psapp:
                print("Photoshop is not running")
                return

            doc = psapp.ActiveDocument
            if not doc:
                print("No document is opened.")
                return

            width = doc.width
            height = doc.height
            target_width = int(width - (width % 16))
            target_height = int(height - (height % 16))
            doc.ResizeImage(target_width, target_height)

        except Exception as e:
            print(f"Error resizing: {e}")

    def showdir(self, e):
        target_psd_path = self.PSDPathLineInput.text()
        target_dirpath = self.build_target_path()
        if not target_dirpath:
            return

        if not os.path.isdir(target_dirpath):
            os.makedirs(target_dirpath)

        if platform.system() == "Windows":
            os.startfile(target_dirpath)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", target_dirpath])
        else:
            subprocess.Popen(["xdg-open", target_dirpath])

    def start(self, e):
        target_psd_path = self.PSDPathLineInput.text()
        self.target_dirpath = self.build_target_path()
        if not self.target_dirpath or \
           not os.path.isdir(self.target_dirpath):
            os.makedirs(self.target_dirpath)

        width_input = self.SaveSizeWidthLineEdit.text()
        height_input = self.SaveSizeHeightLineEdit.text()

        self.target_width = None
        self.target_height = None

        if height_input.isdigit():
            self.target_width = int(width_input)
        else:
            self.target_width = 0

        if height_input.isdigit():
            self.target_height = int(height_input)
        else:
            self.target_height = 0

        self.StartButton.setEnabled(False)
        self.workthread = PSDStoreThreadHolder(
            self.target_dirpath,
            self.PSDPathLineInput.text(),
            self.target_width,
            self.target_height
        )
        self.workthread.finish_signal.connect(self.on_complete)
        self.workthread.start()

    def stop(self, e):
        if self.workthread:
            self.workthread.cancellation_token.emit()
        Thread(target=self.multi_image_write).start()
        self.mainwin.close()

    def on_complete(self, e=None):
        self.StartButton.setEnabled(True)
        if self.workthread:
            self.workthread = None

    def multi_image_write(self):
        def sort_key(path):
            base = os.path.basename(path)
            basename = os.path.splitext(base)[0]
            numbering = basename.split('_')[-1]
            if numbering.isdigit():
                return int(numbering)
            return -1

        target_dir = self.build_target_path()
        if not target_dir:
            return

        target_files = [f"{target_dir}/{x}" for x in os.listdir(target_dir)]
        target_files = list(filter(lambda x: x.endswith(".png"), target_files))
        target_files.sort(key=sort_key)
        imgs = [Image.open(target_file) for target_file in target_files]
        max_width = max([img.size[0] for img in imgs])
        max_height = max([img.size[1] for img in imgs])
        resized_imgs = []
        for img in imgs:
            baseimg = Image.new("RGB", (max_width, max_height), (255, 255, 255))
            left = (baseimg.size[0] / 2) - (img.size[0] / 2)
            top = (baseimg.size[1] / 2) - (img.size[1] / 2)
            rect = (int(left), int(top))
            baseimg.paste(img, rect)
            resized_imgs.append(baseimg)
        arrs = [np.asarray(img) for img in resized_imgs]
        framerate_input = self.FrameRateLineEdit.text()
        target_framerate = 8
        if framerate_input.isdigit():
            target_framerate = int(framerate_input)
        imageio.mimwrite(f"{target_dir}/dst.gif", arrs, fps=target_framerate, loop=0)
        imageio.mimwrite(f"{target_dir}/dst.mp4", arrs, fps=target_framerate)
        print("gif/mp4 save finished!")

    def build_target_path(self):
        target_psd_path = self.PSDPathLineInput.text()
        basename = os.path.basename(target_psd_path)
        target_filename = os.path.splitext(basename)[0]
        if not os.path.isfile(target_psd_path):
            if not os.path.isfile(target_psd_path + ".psd"):
                print("[!] invalid target path")
                return None
            else:
                target_psd_path = target_psd_path + ".psd"
        return f"{os.path.dirname(target_psd_path)}/{target_filename}/recorder"


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    mainwin = QtWidgets.QMainWindow()
    win = WindowHandler(mainwin)
    mainwin.show()
    app.exec()
