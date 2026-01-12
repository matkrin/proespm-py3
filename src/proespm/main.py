import sys

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QApplication

from proespm.gui import MainGui


def main():
    QCoreApplication.setApplicationName("Proespm")

    # icon = QIcon()
    # icon.addFile("proespm_icon_16x16.png")
    # icon.addFile("proespm_icon_24x24.png")
    # icon.addFile("proespm_icon_32x32.png")
    # icon.addFile("proespm_icon_48x48.png")
    # icon.addFile("proespm_icon_64x64.png")
    # icon.addFile("proespm_icon_128x128.png")
    # icon.addFile("proespm_icon_256x256.png")

    app = QApplication(sys.argv)
    # app.setWindowIcon(icon)

    window = MainGui()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
