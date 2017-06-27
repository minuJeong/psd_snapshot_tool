
import os

from PIL import Image


target_width = 496

src = "D:/Temp/Drawing/gafsdgdsaSfdgsbdafdsa/vdsvavdsavdsafdsafdsa/recorder"
dst = "D:/Temp/Drawing/gafsdgdsaSfdgsbdafdsa/vdsvavdsavdsafdsafdsa/resized"

if not os.path.isdir(dst):
    os.makedirs(dst)

for filename in os.listdir(src):
    if not filename.endswith(".png"):
        continue

    src_file = f"{src}/{filename}"
    dst_file = f"{dst}/{filename}"

    img = Image.open(src_file)
    ratio = target_width / img.size[0]

    new_size = (target_width, int(img.size[1] * ratio))
    img = img.resize(new_size, Image.ANTIALIAS)
    img.save(dst_file)
