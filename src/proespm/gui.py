from dataclasses import dataclass
import os
import traceback
from datetime import datetime
from typing import final, override

import matplotlib.pyplot as plt
from PyQt6.QtCore import (
    QObject,
    QRunnable,
    Qt,
    QThreadPool,
    pyqtSignal,
    pyqtSlot,  # pyright: ignore[reportUnknownVariableType]
)
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from proespm.labjournal import parse_labjournal
from proespm.processing import create_html, create_process_objs, process_loop
from proespm.config import Config


@final
class ProcessingWorker(QRunnable):
    """Worker thread for the data processing"""

    def __init__(
        self,
        process_dir: str,
        output_path: str,
        labj_path: str | None,
        colormap: str,
        colorrange: tuple[float, float],
    ) -> None:
        super().__init__()
        self.process_dir = process_dir
        self.output_path = output_path
        self.labj_path = labj_path
        self.config = Config(colormap=colormap, colorrange=colorrange)
        self.signals = WorkerSignals()

    def log(self, message: str) -> None:
        self.signals.message.emit(message)

    @override
    @pyqtSlot()
    def run(self):
        process_dir = self.process_dir
        output_path = self.output_path
        labjournal = (
            parse_labjournal(self.labj_path)
            if self.labj_path is not None
            else None
        )
        report_name = os.path.basename(process_dir)

        try:
            self.log(f"Start processing of {process_dir}")
            process_objs = create_process_objs(process_dir, self.log)
            process_loop(process_objs, labjournal, self.config, self.log)
            create_html(process_objs, labjournal, output_path, report_name)
            self.log(f"HTML created at {output_path}")
            self.signals.finished.emit()

        except Exception:
            self.log(f"An Error occured:\n{traceback.format_exc()}")
            self.signals.finished.emit()


@final
class WorkerSignals(QObject):
    """Class holding the signal.
    Custom signal needs a class derived from QObject!
    """

    message = pyqtSignal(str)
    finished = pyqtSignal()


@final
class MainGui(QMainWindow):
    """Main GUI"""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("proespm")
        self.setGeometry(100, 100, 700, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_layout = QVBoxLayout()
        self.central_widget.setLayout(self.central_layout)

        # Create the grid layout
        grid_layout = QGridLayout()

        # Create label, text input, and button for the first row
        process_dir_label = QLabel("Choose folder: ")
        self.process_dir_input = QLineEdit()
        self.process_dir_input.setReadOnly(True)
        self.process_dir_button = QPushButton("Browse")

        # Add widgets to the grid layout
        grid_layout.addWidget(
            process_dir_label, 0, 0, Qt.AlignmentFlag.AlignLeft
        )
        grid_layout.addWidget(self.process_dir_input, 0, 1)
        grid_layout.addWidget(self.process_dir_button, 0, 2)

        # Create label, text input, and button for the second row
        output_label = QLabel("Output: ")
        self.output_input = QLineEdit()
        self.output_input.setReadOnly(True)
        self.output_button = QPushButton("Save As")

        # Add widgets to the grid layout
        grid_layout.addWidget(output_label, 1, 0, Qt.AlignmentFlag.AlignLeft)
        grid_layout.addWidget(self.output_input, 1, 1)
        grid_layout.addWidget(self.output_button, 1, 2)

        # Set the column stretch to make the text inputs equal in size
        grid_layout.setColumnStretch(1, 1)

        # Add the grid layout to the main layout
        self.central_layout.addLayout(grid_layout)

        # Labjournal Spreadsheet
        labj_layout = QHBoxLayout()
        self.labj_checkbox = QCheckBox(text="Spreadsheet")
        self.labj_checkbox.setCheckState(Qt.CheckState.Unchecked)

        self.labj_input = QLineEdit()
        self.labj_input.setReadOnly(True)
        self.labj_button = QPushButton("Browse")
        self.labj_button.setEnabled(False)
        labj_layout.addWidget(self.labj_checkbox)
        labj_layout.addWidget(self.labj_input)
        labj_layout.addWidget(self.labj_button)
        self.central_layout.addLayout(labj_layout)

        # Colormap
        colormap_layout = QHBoxLayout()
        colormap_lbl = QLabel("Colormap:")
        self.colormap = QComboBox()
        self.colormap.addItems(plt.colormaps())
        self.colormap.setCurrentText("inferno")
        colormap_layout.addWidget(colormap_lbl)
        colormap_layout.addWidget(self.colormap)
        self.central_layout.addLayout(colormap_layout)

        # Color range
        colorrange_layout = QHBoxLayout()
        colorrange_lbl = QLabel("Color range (percentile):")
        self.colorrange_start = QDoubleSpinBox()
        self.colorrange_start.setValue(1.0)
        self.colorrange_end = QDoubleSpinBox()
        self.colorrange_end.setMaximum(100.0)
        self.colorrange_end.setValue(99.0)
        colorrange_layout.addWidget(colorrange_lbl)
        colorrange_layout.addWidget(self.colorrange_start)
        colorrange_layout.addWidget(self.colorrange_end)
        self.central_layout.addLayout(colorrange_layout)

        # Logging area
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        font = QFont("Monospace")
        font.setStyleHint(QFont.StyleHint.TypeWriter)
        font.setPointSize(10)
        self.log_area.setCurrentFont(font)
        self.central_layout.addWidget(self.log_area)

        # Horizontal layout for the save log button
        log_button_layout = QHBoxLayout()
        self.save_log_button = QPushButton("Save Log")
        log_button_layout.addStretch()  # Pushes button to the right
        log_button_layout.addWidget(self.save_log_button)
        self.central_layout.addLayout(log_button_layout)

        # Horizontal layout for the start and exit buttons
        start_exit_button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.start_button.setDefault(True)
        self.exit_button = QPushButton("Exit")
        start_exit_button_layout.addStretch()
        start_exit_button_layout.addWidget(self.start_button)
        start_exit_button_layout.addWidget(self.exit_button)
        start_exit_button_layout.addStretch()
        self.central_layout.addLayout(start_exit_button_layout)

        self.threadpool = QThreadPool()

        self.connect_signals()

    def connect_signals(self):
        """Connect button clicks to their respective function"""
        _ = self.process_dir_button.clicked.connect(self.choose_directory)  # pyright: ignore[reportUnknownMemberType] `pyqtSlot` seems to be not typed
        _ = self.output_button.clicked.connect(self.save_file)  # pyright: ignore[reportUnknownMemberType]
        _ = self.save_log_button.clicked.connect(self.save_log)  # pyright: ignore[reportUnknownMemberType]
        _ = self.exit_button.clicked.connect(self.exit_app)  # pyright: ignore[reportUnknownMemberType]
        _ = self.start_button.clicked.connect(self.start_processing)  # pyright: ignore[reportUnknownMemberType]
        _ = self.labj_checkbox.stateChanged.connect(self.toggle_labj_button)  # pyright: ignore[reportUnknownMemberType]
        _ = self.labj_button.clicked.connect(self.choose_labjournal)  # pyright: ignore[reportUnknownMemberType]

    @pyqtSlot()
    def choose_directory(self) -> None:
        """Handler for `process_dir_button`"""
        dirname = QFileDialog.getExistingDirectory(
            self,
            caption="Choose folder to process",
            directory="",
            options=QFileDialog.Option.ShowDirsOnly,
        )

        if dirname:
            self.process_dir_input.setText(dirname)
            self.log(f"Directory chosen: {dirname}")
            self.output_input.setText(dirname + "_report.html")
        else:
            self.log("No directory chosen.")

    @pyqtSlot()
    def save_file(self) -> None:
        """Handler for `output_button`"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            caption="Save HTML report as...",
            directory="",
            filter="HTML Files (*.html)",
        )

        if file_path:
            self.output_input.setText(file_path)
            self.log(f"File saved as: {file_path}")
        else:
            self.log("No file chosen.")

    @pyqtSlot()
    def save_log(self) -> None:
        """Handler for `save_log_button`"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            caption="Save Log",
            directory="",
            filter="Log Files(*.log);;Text Files (*.txt);;All Files (*)",
        )

        # If a file path is chosen, save the log content to the file
        if file_path:
            with open(file_path, "w") as file:
                _ = file.write(self.log_area.toPlainText())

            self.log(f"Log saved to: {file_path}")

    @pyqtSlot()
    def start_processing(self) -> None:
        self.start_button.setEnabled(False)
        process_dir = self.process_dir_input.text()
        output_path = self.output_input.text()
        is_labj_checked = self.labj_checkbox.isChecked()
        colormap = self.colormap.currentText()
        colorrange = (
            self.colorrange_start.value(),
            self.colorrange_end.value(),
        )

        labj_path = None
        if is_labj_checked and os.path.isfile(self.labj_input.text()):
            labj_path = self.labj_input.text()

        if not os.path.isdir(process_dir):
            _ = QMessageBox.warning(
                self,
                "Error",
                "Please select a valid directory for processing",
            )
            return

        processing_worker = ProcessingWorker(
            process_dir,
            output_path,
            labj_path,
            colormap,
            colorrange,
        )
        _ = processing_worker.signals.message.connect(self.log)  # pyright: ignore[reportUnknownMemberType]
        _ = processing_worker.signals.finished.connect(self.processing_finished)  # pyright: ignore[reportUnknownMemberType]
        self.threadpool.start(processing_worker)

    @pyqtSlot()
    def toggle_labj_button(self) -> None:
        """Handler for labj_checkbox. Toggles labj_button depending on labj_checkbox state"""
        is_checked = self.labj_checkbox.isChecked()
        if is_checked:
            self.labj_button.setEnabled(True)
        else:
            self.labj_button.setEnabled(False)

    @pyqtSlot()
    def choose_labjournal(self) -> None:
        """Handler for `labj_button`"""
        labj_path = QFileDialog.getOpenFileName(
            self,
            caption="Choose Labjournal Spreadsheet",
            directory="",
            filter="Excel files (*.xlsx)",
        )[0]

        if labj_path:
            self.labj_input.setText(labj_path)
            self.log(f"Labjournal chosen: {labj_path}")
        else:
            self.log("No Labjournal chosen.")

    @pyqtSlot()
    def processing_finished(self):
        self.start_button.setEnabled(True)
        self.log_area.append("-" * 40)

    @pyqtSlot()
    def exit_app(self) -> None:
        """Handler for `exit_button`. Exits the app."""
        QApplication.quit()

    def log(self, message: str) -> None:
        """Append `message` to the `log_area`"""
        dt = datetime.now()
        dt_info = dt.strftime("[%Y-%m-%d, %H:%M:%S]:")
        self.log_area.append(f"{dt_info} {message}")
