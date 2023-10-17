import os
from typing import Optional
import datetime

import numpy as np
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import LinearAxis, Range1d


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
        plot = figure(
            width=1000,
            height=540,
            x_axis_label="U vs. ref [V] ",
            y_axis_label="I [A]",
            # x_range=(x[0], x[-1]),
            sizing_mode="scale_width",
            tools="reset, save, wheel_zoom, pan, box_zoom, hover, crosshair",
            active_drag="box_zoom",
            active_scroll="wheel_zoom",
            active_inspect="hover",
        )
        plot.toolbar.logo = None
        plot.background_fill_alpha = 0
        plot.toolbar.active_scroll = "auto"

        x = self.data[:, 1]  # voltage
        y = self.data[:, 2]  # current

        plot.circle(x, y, size=2)

        self.script, self.div = components(plot, wrap_script=True)


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
        plot = figure(
            width=1000,
            height=540,
            x_axis_label="Time [s] ???",
            y_axis_label="I [A]",
            sizing_mode="scale_width",
            tools="reset, save, wheel_zoom, pan, box_zoom, hover, crosshair",
            active_drag="box_zoom",
            active_scroll="wheel_zoom",
            active_inspect="hover",
        )
        plot.toolbar.logo = None
        plot.background_fill_alpha = 0
        plot.toolbar.active_scroll = "auto"

        x = self.data[:, 0]  # time
        y = self.data[:, 2]  # current
        y2 = self.data[:, 1]  # TODO voltage ? not sure

        voltage_min = np.min(self.data[:, 4])
        voltage_min = voltage_min - (abs(voltage_min * 0.05))
        voltage_max = np.max(self.data[:, 4]) * 1.05

        plot.extra_y_ranges["voltage"] = Range1d(voltage_min, voltage_max)
        ax2 = LinearAxis(y_range_name="voltage", axis_label="U [V]")
        ax2.axis_label_text_color = "black"
        plot.add_layout(ax2, "right")

        plot.circle(x, y, size=2, legend_label="I")
        plot.circle(
            x,
            y2,
            size=2,
            legend_label="U",
            color="orange",
            y_range_name="voltage",
        )

        self.script, self.div = components(plot, wrap_script=True)


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
        plot = figure(
            width=1000,
            height=540,
            x_axis_label="Frequency [Hz] ???",
            y_axis_label="Amplitude",
            sizing_mode="scale_width",
            tools="reset, save, wheel_zoom, pan, box_zoom, hover, crosshair",
            active_drag="box_zoom",
            active_scroll="wheel_zoom",
            active_inspect="hover",
        )
        plot.toolbar.logo = None
        plot.background_fill_alpha = 0
        plot.toolbar.active_scroll = "auto"

        data = self.data[self.data[:, 0] < 2000]
        x = data[:, 0]  # frequency
        y = data[:, 1]  # amplitude

        plot.line(x, y)

        self.script, self.div = components(plot, wrap_script=True)
