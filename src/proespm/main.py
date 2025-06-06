import sys

from PyQt6.QtWidgets import QApplication

from proespm.gui import MainGui


def main():
    app = QApplication(sys.argv)
    window = MainGui()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
