
import math
import struct

import numpy as np
from scipy.ndimage import gaussian_filter

from PIL import Image
from pyaudio import PyAudio

from PyQt5 import QtCore


# class GenAudio(QtCore.QThread):
class GenAudio(object):

    BITRATE = 16000
    FREQUENCY = 500
    LENGTH = 2.43215

    # image arrays
    arrs = None

    def __init__(self, arrs):
        super(GenAudio, self).__init__()
        self.arrs = arrs

    def get_luminosity(self, r, g, b):
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    def get_hue(self, r, g, b):
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        xm_delta = max((max_val - min_val), 0.001)
        if r > g and r > b:
            return 0.0 + (g - b) / xm_delta
        elif g > b:
            return 2.0 + (b - r) / xm_delta
        return 4.0 + (r - g) / xm_delta

    def feed(self, loop=False) -> int:
        """
        infinite generator yeids 0 ~ 255
        """

        fp = open("sample.wav", 'rb')
        fp.read(36)

        def debug_txt():
            yield fp.read(2048)

        last_var = 0

        def parse_img(img):
            nonlocal last_var

            for y in range(img.shape[0]):
                for x in range(img.shape[1]):
                    rgb = img[y, x]
                    r = rgb[0] / 255.0
                    g = rgb[1] / 255.0
                    b = rgb[2] / 255.0

                    lum = self.get_luminosity(r, g, b)
                    hue = self.get_hue(r, g, b)
                    mean = np.mean((r, g, b))

                    frequency = max(lum ** 0.15, 0.1)

                    print(lum, hue, frequency)

                    # play a pixel
                    SOUND_SCALE = 25.0
                    for a in np.arange(0.0, math.pi * 2.0, frequency):
                        r_sound = int(((math.sin(a) * r) + r) * SOUND_SCALE)
                        g_sound = int(((math.cos(a) * g) + g) * SOUND_SCALE)
                        b_sound = int(((math.sin(a) * b) + b) * SOUND_SCALE)
                        value = r_sound + g_sound + b_sound
                        yield value

        if self.arrs:
            while True:
                for img in self.arrs:
                    for _ in debug_txt():
                        yield _

                    continue

                    for _ in parse_img(img):
                        yield _

                if not loop:
                    break

        while True:
            last_var *= 0.95
            yield int(last_var)

    def run(self):
        count_frames = self.BITRATE * self.LENGTH
        feeder = self.feed(True)
        data = []
        for _ in range(int(count_frames)):
            frames = next(feeder)
            data.append(frames)
        audio = PyAudio()
        stream = audio.open(format=8,
                            channels=1,
                            rate=16000,
                            output=True)

        for frames in data:
            stream.write(frames)
        stream.stop_stream()
        stream.close()
        audio.terminate()


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
        audio_gen_thread = GenAudio(self.arrs)
        audio_gen_thread.start()
        imageio.mimwrite(f"{self.target_dir}/dst.mp4", self.arrs, fps=self.target_framerate)



if __name__ == "__main__":
    import os
    path = "D:/Temp/Drawing/CUR/a344errdfrfss/recorder"
    filenames = [f"{path}/{filename}" for filename in os.listdir(path)]
    filenames = list(filter(lambda x: x.endswith(".jpg"), filenames))
    filenames = filenames[-5:]
    images = [Image.open(filename) for filename in filenames]
    resized_images = [img.resize((64, 32)) for img in images]
    arrs = [np.asarray(image) for image in resized_images]
    GenAudio(arrs).run()
