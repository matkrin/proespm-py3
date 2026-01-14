import io
import os
from datetime import datetime
from typing import Self, cast, final, override

import numpy as np
from bokeh.embed import components
from numpy._typing import NDArray

from proespm.config import Config
from proespm.ec.ec import EcPlot
from proespm.fileinfo import Fileinfo
from proespm.measurement import Measurement


@final
class CvLabview(Measurement):
    """Class handeling the CV files from self-written LabView software"""

    ident = "CV_LABVIEW"

    def __init__(self, filepath: str) -> None:
        self.fileinfo = Fileinfo(filepath)

        self.type: str | None = None
        self.data = self.read_cv_data(filepath)
        self.u_start: float | None = None
        self.u_1: float | None = None
        self.u_2: float | None = None
        self.rate: float | None = None
        self.read_params()

        assert self.u_1 is not None and self.u_2 is not None  # Type assertion

        tol = 0.002 * (self.u_1 - self.u_2)
        self.cycles = self.split_cycles(tol)

        self.script: str | None = None
        self.div: str | None = None

    def read_cv_data(self, filepath: str) -> NDArray[np.float64]:
        """Read the numeric data as numpy array"""

        with open(filepath, "rb") as f:
            raw = f.read()

        raw = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")

        return np.loadtxt(io.BytesIO(raw), skiprows=1)

    def read_params(self) -> None:
        """Calculate relevent parameters"""
        self.u_start = self.data[0, 1]

        self.u_1 = float(np.max(self.data[:, 1]))
        self.u_2 = float(np.min(self.data[:, 1]))
        if self.data[0, 1] < self.data[1, 1]:
            self.u_1, self.u_2 = self.u_2, self.u_1

        total_time = cast(float, self.data[-1, 0])
        self.rate = 2 * (abs(self.u_1) + abs(self.u_2)) / total_time

    def split_cycles(
        self, tol: float = 0.0
    ) -> list[tuple[NDArray[np.float64], NDArray[np.float64]]]:
        x = self.data[:, 1]  # voltage
        y = self.data[:, 2]  # current

        # Initial scan direction
        d0 = np.sign(x[1] - x[0])  # pyright: ignore[reportAny]
        if d0 == 0:
            raise ValueError("Initial scan direction cannot be zero")

        x0 = x[0]  # pyright: ignore[reportAny]
        cycle_start_indices = [0]

        for i in range(1, len(x)):
            dx = x[i] - x[i - 1]  # pyright: ignore[reportAny]
            d = np.sign(dx)  # pyright: ignore[reportAny]

            # Ignore zero steps, Crossing must happen in initial scan direction
            if d == 0 or d != d0:
                continue

            if d0 > 0:
                crossed = (x[i - 1] < x0 - tol) and (x[i] >= x0 - tol)  # pyright: ignore[reportAny]
            else:
                crossed = (x[i - 1] > x0 + tol) and (x[i] <= x0 + tol)  # pyright: ignore[reportAny]

            if crossed:
                cycle_start_indices.append(i)

        cycles: list[tuple[NDArray[np.float64], NDArray[np.float64]]] = []
        for i in range(len(cycle_start_indices) - 1):
            i0 = cycle_start_indices[i]
            i1 = cycle_start_indices[i + 1]
            cycles.append((x[i0:i1], y[i0:i1]))

        return cycles

    # def plot(self) -> None:
    #     """Create a plot for use in the html-report"""
    #     plot = EcPlot()
    #     plot.set_x_axis_label("U vs. ref [V] ")
    #     plot.set_y_axis_label("I [A]")

    #     x = self.data[:, 1]  # voltage
    #     y = self.data[:, 2]  # current

    #     plot.plot_scatter(x, y)
    #     plot.show_legend(False)

    #     self.script, self.div = components(plot.fig, wrap_script=True)

    def plot(self) -> None:
        plot = EcPlot()
        plot.set_x_axis_label("U vs. ref [V]")
        plot.set_y_axis_label("I [A]")

        for i, arr in enumerate(self.cycles):
            x = arr[0]  # volage
            y = arr[1]  # current

            plot.plot_scatter(x, y, legend_label=f"Cycle {i + 1}")

        plot.set_legend_location("bottom_right")
        self.script, self.div = components(plot.fig, wrap_script=True)

    @override
    def m_id(self) -> str:
        return self.fileinfo.filename

    @override
    def datetime(self) -> datetime:
        return datetime.fromtimestamp(os.path.getmtime(self.fileinfo.filepath))

    @override
    def process(self, config: Config) -> Self:
        self.plot()
        return self

    @override
    def template_name(self) -> str:
        return "ec4.j2"


@final
class CaLabview(Measurement):
    """Class handeling the CA files from self-written LabView software"""

    ident = "CA_LABVIEW"

    def __init__(self, filepath: str) -> None:
        self.fileinfo = Fileinfo(filepath)

        self.type: str | None = None
        self.data = self.read_ca_data(filepath)
        self.u_start: float | None = None
        self.u_1: float | None = None
        self.u_2: float | None = None
        self.rate: float | None = None
        # self.read_params()

        self.script: str | None = None
        self.div: str | None = None

    def read_ca_data(self, filepath: str) -> NDArray[np.float64]:
        """Read the numeric data as numpy array"""

        with open(filepath, "rb") as f:
            raw = f.read()

        raw = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")

        return np.loadtxt(io.BytesIO(raw), skiprows=1)

    def read_params(self) -> None:
        """Calculate relevent parameters"""
        self.u_start = self.data[0, 1]

        self.u_1 = float(np.max(self.data[:, 1]))
        self.u_2 = float(np.min(self.data[:, 1]))
        if self.data[0, 1] < self.data[1, 1]:
            self.u_1, self.u_2 = self.u_2, self.u_1

        total_time = cast(float, self.data[-1, 0])
        self.rate = 2 * (abs(self.u_1) + abs(self.u_2)) / total_time

    def plot(self) -> None:
        """Create a plot for use in the html-report"""
        plot = EcPlot()
        plot.set_x_axis_label("Time [s]")
        plot.set_y_axis_label("I_WE [A]")

        x = self.data[:, 0]  # time
        y = self.data[:, 2]  # current
        y2 = self.data[:, 1]  # voltage

        voltage_range = np.max(self.data[:, 1]) - np.min(self.data[:, 1])
        voltage_range_min = np.min(self.data[:, 1]) - voltage_range * 0.05
        voltage_range_max = np.max(self.data[:, 1]) + voltage_range * 0.05

        current_range = np.max(self.data[:, 2]) - np.min(self.data[:, 2])
        current_range_min = np.min(self.data[:, 2]) - current_range * 0.05
        current_range_max = np.max(self.data[:, 2]) + current_range * 0.05

        plot.add_second_axis(
            "voltage",
            float(voltage_range_min),
            float(voltage_range_max),
            "U_WE [V]",
        )

        plot.plot_scatter(
            x,
            y,
            legend_label="I_WE",
            range_min=float(current_range_min),
            range_max=float(current_range_max),
        )
        plot.plot_second_axis(x, y2, legend_label="U_WE")
        plot.show_legend(True)

        self.script, self.div = components(plot.fig, wrap_script=True)

    @override
    def m_id(self) -> str:
        return self.fileinfo.filename

    @override
    def datetime(self) -> datetime:
        return datetime.fromtimestamp(os.path.getmtime(self.fileinfo.filepath))

    @override
    def process(self, config: Config) -> Self:
        self.plot()
        return self

    @override
    def template_name(self) -> str:
        return "ec4.j2"


@final
class FftLabview(Measurement):
    """Class handeling the FFT files from self-written LabView software"""

    ident = "FFT_LABVIEW"

    def __init__(self, filepath: str) -> None:
        self.fileinfo = Fileinfo(filepath)

        self.type: str | None = None
        self.data = self.read_fft_data(filepath)

        self.script = str | None
        self.div = str | None

    def read_fft_data(self, filepath: str) -> NDArray[np.float64]:
        """Read the numeric data as numpy array"""

        with open(filepath, "rb") as f:
            raw = f.read()

        raw = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")

        return np.loadtxt(io.BytesIO(raw), skiprows=1)

    def plot(self) -> None:
        """Create a plot for use in the html-report"""
        plot = EcPlot()
        plot.set_x_axis_label("Frequence [Hz]")
        plot.set_y_axis_label("Amplitude")

        x = self.data[:, 0]  # frequency
        y = self.data[:, 1]  # amplitude

        plot.plot_line(x, y)

        self.script, self.div = components(plot.fig, wrap_script=True)

    @override
    def m_id(self) -> str:
        return self.fileinfo.filename

    @override
    def datetime(self) -> datetime:
        return datetime.fromtimestamp(os.path.getmtime(self.fileinfo.filepath))

    @override
    def process(self, config: Config) -> Self:
        self.plot()
        return self

    @override
    def template_name(self) -> str:
        return "ec4.j2"
