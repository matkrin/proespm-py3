import os
from datetime import datetime

import numpy as np
from bokeh.embed import components
from bokeh.layouts import row
from bokeh.plotting import figure

from prosurf.fileinfo import Fileinfo


class Qcmb:
    def __init__(self, filepath: str) -> None:
        self.ident = "QCMB"
        self.fileinfo = Fileinfo(filepath)
        self.datetime = datetime.fromtimestamp(os.path.getmtime(filepath))
        self.m_id = self.fileinfo.filename

        arr = np.genfromtxt(
            filepath, delimiter=", ", skip_header=2, skip_footer=1
        )
        self.time = arr[:, 0]  # in s
        self.rate = arr[:, 1]  # in A/s
        self.thickness = arr[:, 2]  # in A
        self.script = None
        self.div = None

    def plot(self) -> None:
        """Plot with two subplots for thickness and rate"""

        subplot_rate = figure(
            width=1000,
            height=700,
            x_axis_label="Time / s",
            y_axis_label="Rate / A/s",
            sizing_mode="scale_width",
            tools="reset, save, wheel_zoom, pan, box_zoom, hover, crosshair",
            active_drag="box_zoom",
            active_scroll="wheel_zoom",
            active_inspect="hover",
        )
        subplot_rate.toolbar.logo = None  # pyright: ignore[reportAttributeAccessIssue]
        subplot_rate.background_fill_alpha = 0
        # plot.circle(x, y, size=2)
        _ = subplot_rate.line(self.time, self.rate, line_width=2)
        subplot_rate.toolbar.active_scroll = "auto"  # pyright: ignore[reportAttributeAccessIssue]

        subplot_thick = figure(
            width=1000,
            height=700,
            x_axis_label="Time / s",
            y_axis_label="Thickness / A",
            sizing_mode="scale_width",
            tools="reset, save, wheel_zoom, pan, box_zoom, hover, crosshair",
            active_drag="box_zoom",
            active_scroll="wheel_zoom",
            active_inspect="hover",
        )
        subplot_thick.toolbar.logo = None  # pyright: ignore[reportAttributeAccessIssue]
        subplot_thick.background_fill_alpha = 0
        # plot.circle(x, y, size=2)
        _ = subplot_thick.line(
            self.time, self.thickness, line_color="seagreen", line_width=2
        )
        subplot_thick.toolbar.active_scroll = "auto"  # pyright: ignore[reportAttributeAccessIssue]

        plot = row(subplot_rate, subplot_thick, sizing_mode="scale_width")

        self.script, self.div = components(plot, wrap_script=True)

    def process(self):
        self.plot()
