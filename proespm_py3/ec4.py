from __future__ import annotations
import os
import re
from dateutil import parser
import itertools
from pathlib import Path
from typing import Optional
import numpy as np
from numpy._typing import NDArray
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.palettes import Category10_10
from bokeh.models import LinearAxis, Range1d


DATETIME_REGEX = re.compile(r"dateTime(\s+[\d\s:-]+)")
U_START_REGEX = re.compile(r"Start(\s+[\d.-]+)")
U1_REGEX = re.compile(r"V1(\s+[\d.-]+)")
U2_REGEX = re.compile(r"V2(\s+[\d.-]+)")
RATE_REGEX = re.compile(r"Rate(\s+[\d.-]+)")


class Ec4:
    def __init__(self, filepath: str | Path) -> None:
        self.filepath = filepath
        self.basename = os.path.basename(filepath)
        self.dirname = os.path.dirname(filepath)
        self.filename, self.fileext = os.path.splitext(self.basename)
        self.m_id = self.filename

        self.read_params()
        self.type: Optional[str] = None
        self.data: list[NDArray[np.float32]] = [self.read_cv_data(filepath)]

    def read_cv_data(self, filepath: str | Path) -> NDArray:
        return np.loadtxt(filepath, skiprows=96)

    def push_cv_data(self, other: Ec4) -> None:
        for arr in other.data:
            self.data.append(arr)

    def read_params(self) -> None:
        with open(self.filepath) as f:
            content = f.read()
            datetime_match = DATETIME_REGEX.search(content)
            u_start_match = U_START_REGEX.search(content)
            u1_match = U1_REGEX.search(content)
            u2_match = U2_REGEX.search(content)
            rate_match = RATE_REGEX.search(content)
            self.datetime = parser.parse(datetime_match.group(1).strip())  # type: ignore
            self.u_start = float(u_start_match.group(1).strip())  # type: ignore
            self.u_1 = float(u1_match.group(1).strip())  # type: ignore
            self.u_2 = float(u2_match.group(1).strip()) # type: ignore
            self.rate = float(rate_match.group(1).strip())  # type: ignore


    def plot(self):
        if self.type == "ca_ec4":
            self.plot_ca()
            return

        colors = itertools.cycle(Category10_10)
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

        for i, arr in enumerate(self.data):
            x = arr[:, 1]  # volage
            y = arr[:, 2]  # current

            plot.circle(
                x, y, size=2, legend_label=f"Cycle {i + 1}", color=next(colors)
            )

        plot.legend.location = "bottom_right"
        self.script, self.div = components(plot, wrap_script=True)

    def plot_ca(self):
        colors = itertools.cycle(Category10_10)
        current_min = np.min([np.min(arr[:, 2]) for arr in self.data])
        current_min = current_min - (abs(current_min * 5))
        current_max = np.max([np.max(arr[:, 2]) for arr in self.data]) * 1.05

        plot = figure(
            width=1000,
            height=540,
            x_axis_label="Time [s]",
            y_axis_label="I [A]",
            # x_range=(x[0], x[-1]),
            y_range=(current_min, current_max),
            sizing_mode="scale_width",
            tools="reset, save, wheel_zoom, pan, box_zoom, hover, crosshair",
            active_drag="box_zoom",
            active_scroll="wheel_zoom",
            active_inspect="hover",
        )
        plot.toolbar.logo = None
        plot.background_fill_alpha = 0
        plot.toolbar.active_scroll = "auto"

        voltage_min = np.min([np.min(arr[:, 1]) for arr in self.data])
        voltage_min = voltage_min - (abs(voltage_min * 0.05))
        voltage_max = np.max([np.max(arr[:, 1]) for arr in self.data]) * 1.05

        plot.extra_y_ranges["voltage"] = Range1d(voltage_min, voltage_max)
        ax2 = LinearAxis(y_range_name="voltage", axis_label="U [V]")
        ax2.axis_label_text_color ="black"
        plot.add_layout(ax2, 'right')

        for i, arr in enumerate(self.data):
            x = arr[:, 0]  # time
            y = arr[:, 2]  # current
            y2 = arr[:, 1]  # voltage

            plot.circle(
                x, y, size=2, legend_label=f"I {i + 1}", color=next(colors)
            )
            plot.circle(
                x, y2, size=2, legend_label=f"U {i + 1}", color=next(colors), y_range_name="voltage"
            )

        self.script, self.div = components(plot, wrap_script=True)
