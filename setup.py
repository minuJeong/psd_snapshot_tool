
import os

from cx_Freeze import setup
from cx_Freeze import Executable


tcl_lib = r"C:\Users\Minu Jeong\AppData\Local\Programs\Python\Python36\tcl\tcl8.6"
tk_lib = r"C:\Users\Minu Jeong\AppData\Local\Programs\Python\Python36\tcl\tk8.6"

os.environ['TCL_LIBRARY'] = tcl_lib
os.environ['TK_LIBRARY'] = tk_lib

# fix numpy build error
addtional_mods = ['numpy.core._methods', 'numpy.lib.format']

setup(
    name="Recorder",
    version="0.0.2",
    package_data={'': ["ffmpeg.exe"]},
    options={'build_exe': {'includes': addtional_mods}},
    executables=[Executable("record.py")]
)
