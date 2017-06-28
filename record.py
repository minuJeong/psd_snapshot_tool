
"""
dependency
 - PyQt5
 - win32com
 - Pillow
 - imagehash
 - psd_tools

"""

import os
import time
import datetime
from threading import Thread
from threading import Lock
from threading import active_count

import imagehash
from psd_tools import PSDImage

from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal
from PyQt5.Qt import Qt
from PyQt5.QtGui import QIntValidator

from win32com import client


class CONST(object):
    DOCUMENT = client.Dispatch("Photoshop.Application").Application.ActiveDocument
    DEFAULT_PATH = f"{DOCUMENT.path}{DOCUMENT.name}"


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

        self.save_success_signal.emit()
        print("Snapshot!")


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

            time.sleep(1.5)

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


class WindowHandler(QtWidgets.QWidget):

    workthread = None

    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.root_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.root_layout)
        self.build_ui()

        self.resize(340, 100)

    def build_ui(self):
        self.psd_path_lineedit = QtWidgets.QLineEdit()
        self.start_btn = QtWidgets.QPushButton("Start")
        self.start_btn.setMinimumHeight(50)

        self.stop_btn = QtWidgets.QPushButton("Stop")
        self.stop_btn.setMinimumHeight(50)

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
        self.root_layout.addWidget(self.stop_btn)

        self.psd_path_lineedit.setText(CONST.DEFAULT_PATH)

        self.start_btn.clicked.connect(self.start)
        self.stop_btn.clicked.connect(self.stop)

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

        target_width = int(self.savesize_width.text())
        target_height = int(self.savesize_height.text())

        self.start_btn.setEnabled(False)
        self.workthread = PSDStoreThreadHolder(
            target_dirpath,
            target_psd_path,
            target_width,
            target_height
        )
        self.workthread.finish_signal.connect(self.on_complete)
        self.workthread.start()

    def stop(self, e):
        if self.workthread:
            self.workthread.cancellation_token.emit()

    def on_complete(self, e=None):
        self.start_btn.setEnabled(True)
        self.workthread = None


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    win = WindowHandler()
    win.show()
    app.exec()
