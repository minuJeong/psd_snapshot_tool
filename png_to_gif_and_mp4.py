
import os

import numpy as np
import imageio
from PIL import Image


target_dir = "D:/Temp/Drawing/gafsdgdsaSfdgsbdafdsa/avvdsavdsa/recorder"
target_files = [f"{target_dir}/{x}" for x in os.listdir(target_dir)]
target_files.sort(key=lambda x: int(os.path.splitext(x)[0].split('_')[-1]))
imgs = [Image.open(target_file) for target_file in target_files]
arrs = [np.asarray(img) for img in imgs]
imageio.mimwrite("dst.gif", arrs, fps=24, loop=0)
imageio.mimwrite("dst.mp4", arrs, fps=24)
