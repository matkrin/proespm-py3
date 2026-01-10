from __future__ import annotations

import itertools
import re
from datetime import datetime
from typing import Self, final, override

import numpy as np
from bokeh.embed import components
from bokeh.palettes import Category10_10
from dateutil import parser
from numpy._typing import NDArray

from proespm.ec.ec import EcPlot
from proespm.fileinfo import Fileinfo
from proespm.config import Config
from proespm.measurement import Measurement


DATETIME_REGEX = re.compile(r"dateTime(\s+[\d\s:-]+)")
U_START_REGEX = re.compile(r"Start(\s+[\d.-]+)")
U1_REGEX = re.compile(r"V1(\s+[\d.-]+)")
U2_REGEX = re.compile(r"V2(\s+[\d.-]+)")
RATE_REGEX = re.compile(r"Rate(\s+[\d.-]+)")


@final
class Ec4(Measurement):
    """Class for handling Nordic Electrochemistry EC4 files (.txt)"""

    ident = "EC4"

    def __init__(self, filepath: str) -> None:
        self.fileinfo = Fileinfo(filepath)

        self._datetime: datetime | None = None
        self.u_start: float | None = None
        self.u_1: float | None = None
        self.u_2: float | None = None
        self.rate: float | None = None
        self.read_params()

        self.ec_type: str | None = None

        self.data: list[NDArray[np.float64]] = [self.read_cv_data(filepath)]
        self.script: str | None = None
        self.div: str | None = None

    def read_cv_data(self, filepath: str) -> NDArray[np.float64]:
        return np.loadtxt(filepath, skiprows=96)

    def push_cv_data(self, other: Ec4) -> None:
        for arr in other.data:
            self.data.append(arr)

    def read_params(self) -> None:
        with open(self.fileinfo.filepath) as f:
            content = f.read()
            datetime_match = DATETIME_REGEX.search(content)
            u_start_match = U_START_REGEX.search(content)
            u1_match = U1_REGEX.search(content)
            u2_match = U2_REGEX.search(content)
            rate_match = RATE_REGEX.search(content)
            if datetime_match is not None:
                self._datetime = parser.parse(datetime_match.group(1).strip())
            if u_start_match is not None:
                self.u_start = float(u_start_match.group(1).strip())
            if u1_match is not None:
                self.u_1 = float(u1_match.group(1).strip())
            if u2_match is not None:
                self.u_2 = float(u2_match.group(1).strip())
            if rate_match is not None:
                self.rate = float(rate_match.group(1).strip())

    def plot(self):
        # Unfortunately, we cannot tell the type by the file ifself, external info needed
        if self.ec_type == "ca_ec4":
            self.plot_ca()
            return

        plot = EcPlot()
        plot.set_x_axis_label("U vs. ref [V]")
        plot.set_y_axis_label("I [A]")

        for i, arr in enumerate(self.data):
            x = arr[:, 1]  # volage
            y = arr[:, 2]  # current

            plot.plot_scatter(x, y, legend_label=f"Cycle {i + 1}")

        plot.set_legend_location("bottom_right")
        self.script, self.div = components(plot.fig, wrap_script=True)

    def plot_ca(self):
        _colors = itertools.cycle(Category10_10)
        current_min = np.min([np.min(arr[:, 2]) for arr in self.data])
        current_min = float(current_min - (abs(current_min * 5)))
        current_max = float(
            np.max([np.max(arr[:, 2]) for arr in self.data]) * 1.05
        )

        plot = EcPlot()
        plot.set_x_axis_label("Time [s]")
        plot.set_y_axis_label("I [A]")
        plot.set_y_range(current_min, current_max)
        """
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
        """

        voltage_min = np.min([np.min(arr[:, 1]) for arr in self.data])
        voltage_min = float(voltage_min - (abs(voltage_min * 0.05)))
        voltage_max = float(
            np.max([np.max(arr[:, 1]) for arr in self.data]) * 1.05
        )

        plot.add_second_axis(
            "voltage", voltage_min, voltage_max, axis_label="U [V]"
        )

        for i, arr in enumerate(self.data):
            x = arr[:, 0]  # time
            y = arr[:, 2]  # current
            y2 = arr[:, 1]  # voltage

            plot.plot_scatter(x, y, legend_label=f"I {i + 1}")
            plot.plot_second_axis(
                x,
                y2,
                legend_label=f"U {i + 1}",
            )

        self.script, self.div = components(plot.fig, wrap_script=True)

    @override
    def m_id(self) -> str:
        return self.fileinfo.filename

    @override
    def datetime(self) -> datetime:
        assert self._datetime is not None  # Type assertion
        return self._datetime

    @override
    def process(self, config: Config) -> Self:
        self.plot()
        return self

    @override
    def template_name(self) -> str:
        return "ec4.j2"
