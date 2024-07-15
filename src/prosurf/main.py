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

from pathlib import Path

from prosurf.spm.mtrx import StmMatrix

def main():
    # app = QApplication(sys.argv)
    # window = MainGui()
    # window.show()
    # sys.exit(app.exec())
    f = "/home/matthias/github/proespm-py3/tests/test_files/20201111--4_1.Z_mtrx"
    m = StmMatrix(f)


if __name__ == "__main__":
    main()
