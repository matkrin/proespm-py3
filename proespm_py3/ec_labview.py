import os
import re
from typing import Optional
from dateutil import parser

import numpy as np
from bokeh.plotting import figure
from bokeh.embed import components


CV_LV_HEADER_LENGTH = 22
DATE_REGEX = re.compile(r"Date\s+[\d\s\/]+")
TIME_REGEX = re.compile(r"Time\s+[\d\s:\.]+")


class CvLabview:
    def __init__(self, filepath):
        self.filepath = filepath
        self.basename = os.path.basename(filepath)
        self.dirname = os.path.dirname(filepath)
        self.filename, self.fileext = os.path.splitext(self.basename)
        self.m_id = self.filename

        self.type: Optional[str] = None
        self.data = self.read_cv_data(filepath)
        self.read_params()

    def read_cv_data(self, filepath):
        return np.loadtxt(filepath, skiprows=CV_LV_HEADER_LENGTH)

    def read_params(self):
        with open(self.filepath) as f:
            content = f.read()

        date_match = DATE_REGEX.search(content)
        print(date_match)
        time_match = TIME_REGEX.search(content)
        self.datetime = parser.parse(f"{date_match.group(0).split()[1].strip()} {time_match.group(0).split()[1].strip()}")  # type: ignore
        print(self.datetime)

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

        x = self.data[:, 1]  # volage
        y = self.data[:, 2]  # current

        plot.circle(x, y, size=2)

        self.script, self.div = components(plot, wrap_script=True)


class CaLabview:
    pass


class FftLabview:
    pass
