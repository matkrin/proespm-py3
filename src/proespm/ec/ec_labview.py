import os
from datetime import datetime
from typing import Self

import numpy as np
from bokeh.embed import components
from numpy._typing import NDArray

from proespm.ec.ec import EcPlot
from proespm.fileinfo import Fileinfo
from proespm.labjournal import Labjournal


class CvLabview:
    """Class handeling the CV files from self-written LabView software"""

    ident = "CV_LABVIEW"

    def __init__(self, filepath: str) -> None:
        self.fileinfo = Fileinfo(filepath)
        self.m_id = self.fileinfo.filename
        self.labjournal_data: dict[str, str] | None = None
        self.datetime = datetime.fromtimestamp(os.path.getmtime(filepath))

        self.type: str | None = None
        self.data = self.read_cv_data(filepath)
        self.u_start: float | None = None
        self.u_1: float | None = None
        self.u_2: float | None = None
        self.rate: float | None = None
        self.read_params()

        self.script: str | None = None
        self.div: str | None = None

    def read_cv_data(self, filepath: str) -> NDArray[np.float64]:
        """Read the numeric data as numpy array"""
        return np.loadtxt(filepath, skiprows=1)

    def read_params(self) -> None:
        """Calculate relevent parameters"""
        self.u_start = self.data[0, 1]

        self.u_1 = float(np.max(self.data[:, 1]))
        self.u_2 = float(np.min(self.data[:, 1]))
        if self.data[0, 1] < self.data[1, 1]:
            self.u_1, self.u_2 = self.u_2, self.u_1

        total_time: float = self.data[-1, 0]
        self.rate = 2 * (abs(self.u_1) + abs(self.u_2)) / total_time

    def plot(self) -> None:
        """Create a plot for use in the html-report"""
        plot = EcPlot()
        plot.set_x_axis_label("U vs. ref [V] ")
        plot.set_y_axis_label("I [A]")

        x = self.data[:, 1]  # voltage
        y = self.data[:, 2]  # current

        plot.plot_scatter(x, y)
        plot.show_legend(False)

        self.script, self.div = components(plot.fig, wrap_script=True)

    def process(self) -> Self:
        self.plot()
        return self

    def set_labjournal_data(self, labjournal: Labjournal) -> None:
        self.labjournal_data = labjournal.extract_metadata_for_m_id(self.m_id)


class CaLabview:
    """Class handeling the CA files from self-written LabView software"""

    ident = "CA_LABVIEW"

    def __init__(self, filepath: str) -> None:
        self.fileinfo = Fileinfo(filepath)
        self.m_id = self.fileinfo.filename
        self.labjournal_data: dict[str, str] | None = None
        self.datetime = datetime.fromtimestamp(os.path.getmtime(filepath))

        self.type: str | None = None
        self.data = self.read_ca_data()
        self.u_start: float | None = None
        self.u_1: float | None = None
        self.u_2: float | None = None
        self.rate: float | None = None
        self.read_params()

        self.script: str | None = None
        self.div: str | None = None

    def read_ca_data(self) -> NDArray[np.float64]:
        """Read the numeric data as numpy array"""
        return np.loadtxt(self.fileinfo.filepath, skiprows=1)

    def read_params(self) -> None:
        """Calculate relevent parameters"""
        self.u_start = self.data[0, 1]

        self.u_1 = float(np.max(self.data[:, 1]))
        self.u_2 = float(np.min(self.data[:, 1]))
        if self.data[0, 1] < self.data[1, 1]:
            self.u_1, self.u_2 = self.u_2, self.u_1

        total_time: float = self.data[-1, 0]
        self.rate = 2 * (abs(self.u_1) + abs(self.u_2)) / total_time

    def plot(self) -> None:
        """Create a plot for use in the html-report"""
        plot = EcPlot()
        plot.set_x_axis_label("Time [s] ???")
        plot.set_y_axis_label("I [A]")

        x = self.data[:, 0]  # time
        y = self.data[:, 2]  # current
        y2 = self.data[:, 1]  # TODO voltage ? not sure

        voltage_min = np.min(self.data[:, 1])
        voltage_min = voltage_min - (abs(voltage_min * 0.05))
        voltage_max = np.max(self.data[:, 1]) * 1.05

        plot.add_second_axis(
            "voltage", float(voltage_min), float(voltage_max), "U [V]"
        )

        plot.plot_scatter(x, y, legend_label="I")
        plot.plot_second_axis(x, y2, legend_label="U")
        plot.show_legend(True)

        self.script, self.div = components(plot.fig, wrap_script=True)

    def process(self) -> Self:
        self.plot()
        return self

    def set_labjournal_data(self, labjournal: Labjournal) -> None:
        self.labjournal_data = labjournal.extract_metadata_for_m_id(self.m_id)


class FftLabview:
    """Class handeling the FFT files from self-written LabView software"""

    ident = "FFT_LABVIEW"

    def __init__(self, filepath: str) -> None:
        self.fileinfo = Fileinfo(filepath)
        self.m_id = self.fileinfo.filename
        self.labjournal_data: dict[str, str] | None = None
        self.datetime = datetime.fromtimestamp(os.path.getmtime(filepath))

        self.type: str | None = None
        self.data = self.read_fft_data()

        self.script = str | None
        self.div = str | None

    def read_fft_data(self):
        """Read the numeric data as numpy array"""
        return np.loadtxt(self.fileinfo.filepath, skiprows=1)

    def plot(self) -> None:
        """Create a plot for use in the html-report"""
        plot = EcPlot()
        plot.set_x_axis_label("Frequence [Hz]")
        plot.set_y_axis_label("Amplitude")

        x = self.data[:, 0]  # frequency
        y = self.data[:, 1]  # amplitude

        plot.plot_line(x, y)

        self.script, self.div = components(plot.fig, wrap_script=True)

    def process(self) -> Self:
        self.plot()
        return self

    def set_labjournal_data(self, labjournal: Labjournal) -> None:
        self.labjournal_data = labjournal.extract_metadata_for_m_id(self.m_id)
