
"""
Utility class for build ui files.
This script will just compile all ui files into python class

Python version:
 - >=3.6

author: Minu Jeong
"""

import sys
import os

import pysideuic


def run():

    # build qrc files
    dirname = os.path.dirname(__file__)
    for root, dirs, files in os.walk(dirname):
        for ui_filename in files:
            if not ui_filename.endswith(".ui"):
                continue

            src_filename = ui_filename.replace(".ui", "")
            src_path = "{}/{}.qrc".format(
                root,
                src_filename
            )

            if os.path.exists(src_path):
                rcc_compiler = None
                if sys.version[0] == '3':
                    rcc_compiler = "pyrcc5"

                else:
                    rcc_compiler = "pyrcc4"

                os.system("{} -o {}/{}_rc.py {}".format(
                    rcc_compiler,
                    root,
                    src_filename,
                    src_path
                ))

    target_dir = os.path.dirname(__file__).replace("\\", '/')
    pysideuic.compileUiDir(target_dir)

if __name__ == "__main__":
    run()
