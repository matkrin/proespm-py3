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
#

import sys
from PyQt6.QtWidgets import QApplication

from prosurf.gui import MainGui


def main():
    app = QApplication(sys.argv)
    window = MainGui()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
