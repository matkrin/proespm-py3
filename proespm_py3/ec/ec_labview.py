import os
from typing import Optional
import datetime

import numpy as np
from bokeh.embed import components

from proespm_py3.ec.ec import EcPlot


class CvLabview:
    def __init__(self, filepath):
        self.filepath = filepath
        self.basename = os.path.basename(filepath)
        self.dirname = os.path.dirname(filepath)
        self.filename, self.fileext = os.path.splitext(self.basename)
        self.m_id = self.filename
        self.datetime = datetime.datetime.utcfromtimestamp(
            os.path.getmtime(filepath)
        )

        self.type: Optional[str] = None
        self.data = self.read_cv_data(filepath)
        self.read_params()

    def read_cv_data(self, filepath):
        return np.loadtxt(filepath, skiprows=1)

    def read_params(self):
        self.u_start = self.data[0, 1]

        self.u_1 = np.max(self.data[:, 1])
        self.u_2 = np.min(self.data[:, 1])
        if self.data[0, 1] < self.data[1, 1]:
            self.u_1, self.u_2 = self.u_2, self.u_1

        total_time = self.data[-1, 0]
        self.rate = 2 * (abs(self.u_1) + abs(self.u_2)) / total_time

    def plot(self):
        plot = EcPlot()
        plot.set_x_axis_label("U vs. ref [V] ")
        plot.set_y_axis_label("I [A]")

        x = self.data[:, 1]  # voltage
        y = self.data[:, 2]  # current

        plot.plot_circle(x, y)
        plot.show_legend(False)

        self.script, self.div = components(plot.fig, wrap_script=True)


class CaLabview:
    def __init__(self, filepath):
        self.filepath = filepath
        self.basename = os.path.basename(filepath)
        self.dirname = os.path.dirname(filepath)
        self.filename, self.fileext = os.path.splitext(self.basename)
        self.m_id = self.filename
        self.datetime = datetime.datetime.utcfromtimestamp(
            os.path.getmtime(filepath)
        )

        self.type: Optional[str] = None
        self.data = self.read_ca_data(filepath)
        self.read_params()

    def read_ca_data(self, filepath):
        # converter = lambda x: float(x.replace(b",", b"."))
        return np.loadtxt( filepath, skiprows=1)  # type: ignore

    def read_params(self):
        self.u_start = self.data[0, 1]

        self.u_1 = np.max(self.data[:, 1])
        self.u_2 = np.min(self.data[:, 1])
        if self.data[0, 1] < self.data[1, 1]:
            self.u_1, self.u_2 = self.u_2, self.u_1

        total_time = self.data[-1, 0]
        self.rate = 2 * (abs(self.u_1) + abs(self.u_2)) / total_time

    def plot(self):
        plot = EcPlot()
        plot.set_x_axis_label("Time [s] ???")
        plot.set_y_axis_label("I [A]")

        x = self.data[:, 0]  # time
        y = self.data[:, 2]  # current
        y2 = self.data[:, 1]  # TODO voltage ? not sure

        voltage_min = np.min(self.data[:, 1])
        voltage_min = voltage_min - (abs(voltage_min * 0.05))
        voltage_max = np.max(self.data[:, 1]) * 1.05

        plot.add_second_axis("voltage", voltage_min, voltage_max, "U [V]")

        plot.plot_circle(x, y, legend_label="I")
        plot.plot_second_axis(x, y2, legend_label="U")
        plot.show_legend(True)

        self.script, self.div = components(plot.fig, wrap_script=True)


class FftLabview:
    def __init__(self, filepath):
        self.filepath = filepath
        self.basename = os.path.basename(filepath)
        self.dirname = os.path.dirname(filepath)
        self.filename, self.fileext = os.path.splitext(self.basename)
        self.m_id = self.filename
        self.datetime = datetime.datetime.utcfromtimestamp(
            os.path.getmtime(filepath)
        )

        self.type: Optional[str] = None
        self.data = self.read_fft_data(filepath)

    def read_fft_data(self, filepath):
        return np.loadtxt(filepath, skiprows=1)

    def plot(self):
        plot = EcPlot()
        plot.set_x_axis_label("Frequence [Hz]")
        plot.set_y_axis_label("Amplitude")

        data = self.data[self.data[:, 0] < 2000]
        x = data[:, 0]  # frequency
        y = data[:, 1]  # amplitude

        plot.plot_line(x, y)

        self.script, self.div = components(plot.fig, wrap_script=True)
