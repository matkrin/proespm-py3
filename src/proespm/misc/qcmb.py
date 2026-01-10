import os
from datetime import datetime
from typing import Self, final, override

import numpy as np
from bokeh.embed import components
from bokeh.layouts import row
from bokeh.plotting import figure

from proespm.fileinfo import Fileinfo
from proespm.config import Config
from proespm.measurement import Measurement


@final
class Qcmb(Measurement):
    def __init__(self, filepath: str) -> None:
        self.fileinfo = Fileinfo(filepath)

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
        return "qcmb.j2"
