
import os
import time
import datetime
from threading import Thread
from threading import Lock
from threading import active_count

import imagehash
from psd_tools import PSDImage

from PyQt5 import QtWidgets
from PyQt5.QtGui import QIntValidator


class CONST(object):
    DEFAULT_PATH = "D:/Drawing/6fdadfaew 3/rhbafdsafdas.psd"


class PSDStoreThread(Thread):

    psd_path = None
    png_path = None
    override_size = None
    hashlock = None
    last_hash = None

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

            target_ratio = min(w_ratio, h_ratio)
            target_w = int(org_size[0] * target_ratio)
            target_h = int(org_size[1] * target_ratio)

            target_size = (target_w, target_h)
        else:
            target_size = org_size

        as_img = as_img.resize(target_size)
        as_img.save(self.png_path)
        timestamp = datetime.datetime.fromtimestamp(time.time()).strftime("%m-%d %H:%M:%S")
        print(f"[{timestamp}] Saved new snapshot!")


class WindowHandler(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        self.root_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.root_layout)
        self.build_ui()

        self.resize(340, 100)

    def build_ui(self):
        self.psd_path_lineedit = QtWidgets.QLineEdit()
        self.start_btn = QtWidgets.QPushButton("Start")
        self.start_btn.setMinimumHeight(50)

        self.sizecontrol_layout = QtWidgets.QHBoxLayout()
        self.sizecontrol_widget = QtWidgets.QWidget()
        self.sizecontrol_widget.setLayout(self.sizecontrol_layout)

        self.savesize_width = QtWidgets.QLineEdit()
        self.savesize_width.setText("0")
        self.savesize_width.setValidator(QIntValidator(8, 8192))

        self.savesize_height = QtWidgets.QLineEdit()
        self.savesize_height.setText("0")
        self.savesize_height.setValidator(QIntValidator(8, 8192))

        self.sizecontrol_layout.addWidget(QtWidgets.QLabel("Width"))
        self.sizecontrol_layout.addWidget(self.savesize_width)
        self.sizecontrol_layout.addWidget(QtWidgets.QLabel("   "))
        self.sizecontrol_layout.addWidget(QtWidgets.QLabel("Height"))
        self.sizecontrol_layout.addWidget(self.savesize_height)

        self.root_layout.addWidget(self.psd_path_lineedit)
        self.root_layout.addWidget(self.sizecontrol_widget)
        self.root_layout.addWidget(self.start_btn)

        self.psd_path_lineedit.setText(CONST.DEFAULT_PATH)

        self.start_btn.clicked.connect(self.start)

    def start(self, e):
        target_psd_path = self.psd_path_lineedit.text()

        if not os.path.isfile(target_psd_path):
            if not os.path.isfile(target_psd_path + ".psd"):
                print("[!] invalid target path")
                return
            else:
                target_psd_path = target_psd_path + ".psd"

        target_filename = os.path.basename(target_psd_path).replace(".psd", "")
        target_dirpath = \
            f"{os.path.dirname(target_psd_path)}/{target_filename}/recorder"
        if not os.path.isdir(target_dirpath):
            os.makedirs(target_dirpath)

        indexing = 0
        hashlock = Lock()
        last_hash = [None]
        as_img = None

        while True:
            time.sleep(3.0)

            last_hash = last_hash[-1:]
            psd_thread = PSDStoreThread(
                target_psd_path,
                self.get_cachename(target_dirpath, indexing),
                (int(self.savesize_width.text()), int(self.savesize_height.text())),
                hashlock,
                last_hash)
            psd_thread.start()
            indexing += 1

            if active_count() > 2:
                print("[WARNING] thread morethan 2")

    def get_cachename(self, target_dirpath, indexing):
        return f"{target_dirpath}/cached_{indexing}.png"


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    win = WindowHandler()
    win.show()
    app.exec()
