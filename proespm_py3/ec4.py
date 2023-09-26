from __future__ import annotations
import os
import re
from dateutil import parser
import itertools
from typing import Optional
import numpy as np
from numpy._typing import NDArray
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.palettes import Category10_10


DATETIME_REGEX = re.compile(r"dateTime\s+[\d\s:-]+")


class Ec4:
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.basename = os.path.basename(filepath)
        self.dirname = os.path.dirname(filepath)
        self.filename, self.fileext = os.path.splitext(self.basename)
        self.m_id = self.filename
        self.datetime = parser.parse(self.read_datetime())
        self.type: Optional[str] = None
        self.data: list[NDArray] = [self.read_cv_data(filepath)]

    def read_cv_data(self, filepath: str) -> NDArray:
        return np.loadtxt(filepath, skiprows=96)

    def push_cv_data(self, other: Ec4) -> None:
        for arr in other.data:
            self.data.append(arr)

    def read_datetime(self) -> str:
        with open(self.filepath) as f:
            match = DATETIME_REGEX.search(f.read())
            return match.group(0).split("\t")[1].strip()  # type: ignore

    def plot(self):
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
            if self.type == "ca_ec4":
                x = arr[:, 0]
                y = arr[:, 2]
            else:
                x = arr[:, 1]
                y = arr[:, 2]

            plot.circle(
                x, y, size=2, legend_label=f"Cycle {i + 1}", color=next(colors)
            )
            # plot.line(x, y)

        self.script, self.div = components(plot, wrap_script=True)
