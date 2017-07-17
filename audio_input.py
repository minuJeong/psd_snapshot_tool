
import time
from threading import Thread

import pyaudio

from PySide import QtGui
from PySide.QtCore import Qt

from PIL import Image


class Recorder(QtGui.QWidget):

    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    is_recording = False
    is_record_thread_running = False
    frames = None

    def __init__(self):
        super(Recorder, self).__init__()

        self.setWindowFlags(
            Qt.WindowCloseButtonHint |
            Qt.WindowStaysOnTopHint)
        self.setMinimumSize(150, 200)
        self.central_layout = QtGui.QVBoxLayout()
        self.setLayout(self.central_layout)

        self.record_button = QtGui.QPushButton()
        self.record_button.setText("O")
        self.record_button.setMinimumSize(120, 80)
        self.central_layout.addWidget(self.record_button)

        self.play_button = QtGui.QPushButton()
        self.play_button.setText(">")
        self.play_button.setMinimumSize(120, 40)
        self.central_layout.addWidget(self.play_button)

        self.save_button = QtGui.QPushButton()
        self.save_button.setText("ㅁ")
        self.save_button.setMinimumSize(120, 40)
        self.central_layout.addWidget(self.save_button)

        self.record_button.mousePressEvent = self.start_record
        self.record_button.mouseReleaseEvent = self.stop_record

        self.play_button.clicked.connect(self.play_last)
        self.save_button.clicked.connect(self.save_as_file)

    def start_record(self, e=None):
        self.is_recording = True
        record_thread = Thread(target=self.record)
        record_thread.start()

    def stop_record(self, e=None):
        self.is_recording = False

    def play_last(self, e=None):
        if not self.frames:
            return

        audio_output = pyaudio.PyAudio()
        output_stream = audio_output.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            output=True
        )

        for data in self.frames:
            output_stream.write(data)

    def save_as_file(self, e=None):
        self.save().save("save.png")

    def send_to_ps(self):
        # wait for thread complete
        while self.is_record_thread_running:
            time.sleep(0.1)

        print("Sending image to photoshop..")

        img = self.save()
        ps = client.Dispatch("Photoshop.Application")
        app = ps.Application

        doc = None
        try:
            doc = app.ActiveDocument
        except:
            pass

        doc = app.documents.add(img.size[0], img.size[1], 72, "docRef", "RGB")
        print(doc)

    def record(self):
        self.is_record_thread_running = True

        audio_input = pyaudio.PyAudio()
        input_stream = audio_input.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK)

        print("START RECORDING..")
        self.frames = []
        while self.is_recording:
            data = input_stream.read(self.CHUNK)
            self.frames.append(data)
        print("FINISHED RECORDING!")

        input_stream.stop_stream()
        audio_input.terminate()

        self.is_record_thread_running = False

    def save(self):
        if not self.frames:
            return Image.new("L", (1, 1), (0,))

        frame_count = len(self.frames)
        unit = len(self.frames[0])
        data_scale_ratio = int(unit / 2048)

        w_offset_unit = 4
        w_sum = 64 * w_offset_unit * data_scale_ratio
        h_sum = 32 * (int(frame_count / w_offset_unit) * data_scale_ratio + 1)
        img = Image.new("L", (w_sum, h_sum), (128))
        px = img.load()
        for i, frame in enumerate(self.frames):
            w = 64 * data_scale_ratio
            h = 32 * data_scale_ratio
            x_offset = (i % w_offset_unit) * w
            y_offset = int(i / w_offset_unit) * h
            for x in range(w):
                for y in range(h):
                    value = frame[x + (y * w)]
                    px[x + x_offset, y + y_offset] = (value,)
        print("Generated image")

        return img

if __name__ == "__main__":
    app = QtGui.QApplication([])
    recorder = Recorder()
    recorder.show()
    app.exec_()
