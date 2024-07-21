import sys

from PyQt6.QtWidgets import QApplication

from prosurf.gui import MainGui


def main():
    app = QApplication(sys.argv)
    window = MainGui()
    window.show()
    sys.exit(app.exec())

    # f = "/home/matthias/github/proespm-py3/tests/test_files/20201111--4_1.Z_mtrx"
    # f = "/Users/matthias/github/prosurf/tests/testdata/20201111--4_1.Z_mtrx"
    # m = StmMatrix(f)
    # m.process()
    # m.slide_num = 1
    # create_html([m],  "/Users/matthias/github/prosurf/",  "/Users/matthias/github/prosurf/tests/testdata")
    # files_dir = "/Users/matthias/Downloads/matrix_data/2024-07-10"
    #
    # file_lst: list[str] = []
    # for entry in os.scandir(files_dir):
    #     if entry.path.endswith(ALLOWED_FILE_TYPES) and entry.is_file():
    #         file_lst.append(entry.path)
    #
    # slide_num = 1
    # ms: list[ProcessObject] = []
    # for f in file_lst:
    #     if f.endswith("Z_mtrx"):
    #         m = StmMatrix(f)
    #         m.process()
    #         m.slide_num = slide_num
    #         slide_num += 1
    #         ms.append(m)
    #
    # create_html(ms, files_dir, files_dir)


if __name__ == "__main__":
    main()
