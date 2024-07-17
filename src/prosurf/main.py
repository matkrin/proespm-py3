# from pathlib import Path
#
# ALLOWED_FILE_TYPES = (
#     ".mul",
#     ".png",
#     ".txt",
#     ".Z_mtrx",
#     ".flm",
#     ".log",
#     ".SM4",
#     ".dat",
#     ".sxm",
#     ".vms",
#     ".nid",
#     ".jpg",
#     ".jpeg",
#     ".csv",
# )

import sys

from PyQt6.QtWidgets import QApplication

from prosurf.gui import MainGui
from prosurf.html_rendering import create_html
from prosurf.spm.mtrx import StmMatrix

ProcessObject = StmMatrix


def main():
    # app = QApplication(sys.argv)
    # window = MainGui()
    # window.show()
    # sys.exit(app.exec())
    # f = "/home/matthias/github/proespm-py3/tests/test_files/20201111--4_1.Z_mtrx"
    f = "/Users/matthias/github/prosurf/tests/testdata/20201111--4_1.Z_mtrx"
    m = StmMatrix(f)
    m.process()
    m.slide_num = 1
    create_html([m],  "/Users/matthias/github/prosurf/",  "/Users/matthias/github/prosurf/tests/testdata")


if __name__ == "__main__":
    main()
