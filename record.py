
"""
dependency
 - PyQt5
 - win32com
 - Pillow
 - imagehash
 - psd_tools

"""

import os
import shutil
import platform
import time
import datetime
import subprocess
import gc
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
from PyQt5.QtGui import QPixmap

from win32com import client

from ui.record import mainwindow
from palette_handler import PaletteHandler
from gen_mp4 import GenMp4


class CONST(object):
    @property
    def DEFAULT_PATH(self):
        try:
            psapp = client.Dispatch("Photoshop.Application").Application
            doc = psapp.ActiveDocument
            return f"{doc.path}{doc.name}"
        except:
            return None


class PSDStoreThread(QThread):
    psd_path = None
    png_path = None
    override_size = None
    hashlock = None
    last_hash = None

    save_success_signal = pyqtSignal(str)

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

        print("Snapshot!")
        self.save_success_signal.emit(self.png_path)


class PSDStoreThreadHolder(QThread):

    target_dirpath = None
    target_psd_path = None
    target_width = 0
    target_height = 0

    index = 456

    cancellation_token = pyqtSignal()
    before_save_signal= pyqtSignal()
    progress_signal = pyqtSignal(str)
    finish_signal = pyqtSignal()

    cancellation_token_flipped = False

    def __init__(self,
                 target_dirpath, target_psd_path,
                 target_width, target_height,
                 target_file_type):
        super(PSDStoreThreadHolder, self).__init__()
        self.target_dirpath = target_dirpath
        self.target_psd_path = target_psd_path
        self.target_width = target_width
        self.target_height = target_height
        self.target_file_type = target_file_type

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

            self.before_save_signal.emit()

            time.sleep(1.50)

            last_hash = last_hash[-1:]
            psd_thread = PSDStoreThread(
                self.target_psd_path,
                self.get_cachename(),
                (self.target_width, self.target_height),
                hashlock,
                last_hash
            )

            psd_thread.save_success_signal.connect(self.on_save_file)
            psd_thread.start()
            psd_thread.wait()

        # will never happen
        self.finish_signal.emit()

    def on_save_file(self, filepath):
        self.progress_signal.emit(filepath)
        self.index += 1

    def get_cachename(self):
        return f"{self.target_dirpath}/cached_{self.index}.{self.target_file_type}"


class MimRecThread(QThread):

    finish_signal = pyqtSignal()

    def __init__(self, target_dir, target_file_type, target_width, target_height, target_framerate):
        super(MimRecThread, self).__init__()
        self.target_dir = target_dir
        self.target_file_type = target_file_type
        self.target_width = target_width
        self.target_height = target_height
        self.target_framerate = target_framerate

    def run(self):
        def sort_key(path):
            base = os.path.basename(path)
            basename = os.path.splitext(base)[0]
            numbering = basename.split('_')[-1]
            if numbering.isdigit():
                return int(numbering)
            return -1

        if not self.target_dir:
            print("Invalid thread initialize: no target directory")
            return self.finish_signal.emit()

        print("Preparing images..")
        target_files = [f"{self.target_dir}/{x}" for x in os.listdir(self.target_dir)]
        target_files = list(filter(lambda x: x.endswith(f".{self.target_file_type}"), target_files))
        if not target_files:
            print("Quit thread: no target image found")
            return self.finish_signal.emit()

        target_files.sort(key=sort_key)
        raw_imgs = [Image.open(target_file) for target_file in target_files]
        max_width = max([img.size[0] for img in raw_imgs])
        max_height = max([img.size[1] for img in raw_imgs])

        target_ratio = 1.0
        if self.target_width != 0 or self.target_height != 0:
            w_ratio = self.target_width / max_width
            h_ratio = self.target_height / max_height
            target_ratio = min(w_ratio, h_ratio)
        target_width = int(max_width * target_ratio)
        target_height = int(max_height * target_ratio)

        print("Unifying image sizes..")
        paging_dir = ".PAGING"
        if os.path.isdir(paging_dir):
            shutil.rmtree(paging_dir)
            time.sleep(1)
        os.makedirs(paging_dir)

        count = len(raw_imgs)
        for i, img in enumerate(raw_imgs):
            print(f"Resizing: {i + 1} / {count}..")

            # ignore if image already fits target size
            if img.size[0] == target_width and img.size[1] == target_height:
                img.save(f"{paging_dir}/unif_{i}.{self.target_file_type}")
                continue

            resized_img = img
            if not target_ratio == 1.0:
                resized_img = img.resize((target_width, target_height), Image.BICUBIC)

            if resized_img.size[0] == target_width and resized_img.size[1] == target_height:
                resized_img.save(f"{paging_dir}/unif_{i}.{self.target_file_type}")
                continue

            print("DIFFERENT SIZE!")
            baseimg = Image.new("RGB", target_size, (255, 255, 255))
            left = (baseimg.size[0] / 2) - (img.size[0] / 2)
            top = (baseimg.size[1] / 2) - (img.size[1] / 2)
            rect = (int(left), int(top))
            baseimg.paste(img, rect)
            baseimg.save(f"{paging_dir}/unif_{i}.{self.target_file_type}")

            raw_imgs.remove(img)
            del img
            del baseimg

        print("Serializing images..")
        target_files = [f"{paging_dir}/{x}" for x in os.listdir(paging_dir)]
        target_files = list(filter(lambda x: x.endswith(f".{self.target_file_type}"), target_files))
        if not target_files:
            print("no paging file found")
            return self.finish_signal.emit()
        target_files.sort(key=sort_key)

        # append last frame
        [target_files.append(target_files[-1]) for _ in range(20)]
        unified_imgs = [Image.open(target_file) for target_file in target_files]
        arrs = [np.array(img) for img in unified_imgs]
        shutil.rmtree(paging_dir)

        print("starting gif save..")
        imageio.mimwrite(f"{self.target_dir}/dst.gif", arrs, fps=self.target_framerate, loop=0)
        print("Gif Done!")

        gen_mp4_thread = GenMp4(arrs, self.target_dir, self.target_framerate)
        gen_mp4_thread.finish_signal.connect(self.gen_mp4_callback)
        gen_mp4_thread.start()

    def gen_mp4_callback(self):
        self.finish_signal.emit()


class WindowHandler(mainwindow.Ui_MainWindow):

    const = CONST()
    workthread = None

    @property
    def target_file_type(self):
        return self.FileTypeComboBox.currentText()

    @property
    def target_width(self):
        width_input = self.SaveSizeWidthLineEdit.text()
        if width_input.isdigit():
            return min(int(width_input), 1024)
        else:
            return 0

    @property
    def target_height(self):
        height_input = self.SaveSizeHeightLineEdit.text()
        if height_input.isdigit():
            return min(int(height_input), 720)
        else:
            return 0

    @property
    def is_autosave_enabled(self):
        return self.AutoSaveCheckbox.isChecked()

    @property
    def is_closewhendone_enabled(self):
        return self.CloseWhenDoneCheckbox.isChecked()

    @property
    def is_clearcache_enabled(self):
        return self.ClearCacheCheckbox.isChecked()

    @property
    def target_framerate(self):
        input_txt = self.FrameRateLineEdit.text()
        if input_txt.isdigit():
            return int(input_txt)
        else:
            return 8

    def __init__(self, mainwin):
        super(WindowHandler, self).__init__()

        self.mainwin = mainwin

        self.setupUi(self.mainwin)

        self.RefreshPSDirectoryButton.clicked.connect(self.refresh_psd_dirpath)
        self.MakeDivisable16Button.clicked.connect(self.make_divisable_by_16)
        self.ShowDirectoryButton.clicked.connect(self.showdir)
        self.StartButton.clicked.connect(self.start)
        self.StopButton.clicked.connect(self.stop)
        self.PreviewLabel.setPixmap(QPixmap(""))
        self.palette_handler = PaletteHandler(self.PaletteGrpView)

        self.mainwin.setFocusPolicy(Qt.StrongFocus)
        self.mainwin.keyPressEvent = self.keyPressEvent

        self.mainwin.setWindowFlags(self.mainwin.windowFlags() | Qt.WindowStaysOnTopHint)
        self.refresh_psd_dirpath()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Enter:
            mods = QtWidgets.QApplication.keyboardModifiers()
            print(mods)
            if mods == Qt.ShiftModifier:
                print("BVDSVDS")
            e.accept()

    def refresh_psd_dirpath(self, e=None):
        self.PSDPathLineInput.setText(self.const.DEFAULT_PATH)

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

    def showdir(self, e=None):
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

    def start(self, e=None):
        target_psd_path = self.PSDPathLineInput.text()
        if not target_psd_path:
            print("Path not specified")
            return

        self.target_dirpath = self.build_target_path()
        if not os.path.isdir(self.target_dirpath):
            os.makedirs(self.target_dirpath)

        self.StartButton.setEnabled(False)
        self.FileTypeComboBox.setEnabled(False)
        self.workthread = PSDStoreThreadHolder(
            self.target_dirpath,
            self.PSDPathLineInput.text(),
            self.target_width,
            self.target_height,
            self.target_file_type
        )
        self.workthread.before_save_signal.connect(self.on_before_start)
        self.workthread.progress_signal.connect(self.on_progress)
        self.workthread.finish_signal.connect(self.on_complete)
        self.workthread.start()

        self.mainwin.setWindowFlags(self.mainwin.windowFlags() | Qt.WindowStaysOnTopHint)

    def stop(self, e=None):
        # cancel running thread
        if self.workthread:
            self.workthread.cancellation_token.emit()

        target_dir = self.build_target_path()

        def on_save_complete():
            print("multi image serialize process complete, purging..")
            if self.is_closewhendone_enabled:
                self.mainwin.close()
            else:
                self.mainwin.setEnabled(True)

            if self.is_clearcache_enabled:
                cache_files = [f"{target_dir}/{x}" for x in os.listdir(target_dir)]
                cache_files = list(filter(lambda x: x.endswith(self.target_file_type), cache_files))
                cache_files = list(filter(lambda x: "cached_" in os.path.basename(x), cache_files))
            self.showdir()

            print("Purge done!")

        self.mainwin.setEnabled(False)
        self.mim_write_thread = MimRecThread(
            target_dir,
            self.target_file_type,
            self.target_width,
            self.target_height,
            self.target_framerate
        )
        self.mim_write_thread.finish_signal.connect(on_save_complete)
        self.mim_write_thread.start()

    def on_progress(self, snapshot_path):
        try:
            size = self.PreviewLabel.size()
            pixmap = QPixmap(snapshot_path)
            self.PreviewLabel.setPixmap(
                pixmap.scaled(size, Qt.KeepAspectRatio)
            )
        except e as Exception:
            print(e)

    def on_complete(self, e=None):
        self.StartButton.setEnabled(True)
        if self.workthread:
            self.workthread = None

    def on_before_start(self, e=None):
        if self.is_autosave_enabled:
            self.save_photoshop_doc()

    def build_target_path(self):
        target_psd_path = self.PSDPathLineInput.text()
        basename = os.path.basename(target_psd_path)
        target_filename = os.path.splitext(basename)[0]
        if not os.path.isfile(target_psd_path):
            if not os.path.isfile(target_psd_path + ".psd"):
                print("Critical error: invalid target path")
                return None
            else:
                target_psd_path = target_psd_path + ".psd"
        result_path = f"{os.path.dirname(target_psd_path)}/{target_filename}/recorder".replace('\\', '/')
        if not os.path.isdir(result_path):
            os.makedirs(result_path)
        return result_path

    def save_photoshop_doc(self):
        try:
            psapp = client.Dispatch("Photoshop.Application").Application
            doc = psapp.ActiveDocument
            doc.save()
        except:
            return


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    mainwin = QtWidgets.QMainWindow()
    win = WindowHandler(mainwin)
    mainwin.show()
    app.exec()
