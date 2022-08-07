import numpy as np
import os
import datetime
from bokeh.plotting import figure
from bokeh.layouts import row
from bokeh.embed import components


class Qcmb:
    def __init__(self, filepath):
        self.filepath = filepath
        self.basename = os.path.basename(self.filepath)
        self.dirname = os.path.dirname(self.filepath)
        self.filename, self.fileext = os.path.splitext(self.basename)
        self.datetime = datetime.datetime.utcfromtimestamp(
            os.path.getmtime(filepath)
        )
        self.m_id = self.filename

        self.read_qcmb(filepath)

    def read_qcmb(self, filepath):
        """read the txt file produced by stm2 qcmb software"""

        arr = np.genfromtxt(
            filepath, delimiter=", ", skip_header=2, skip_footer=1
        )
        self.time = arr[:, 0]  # in s
        self.rate = arr[:, 1]  # in A/s
        self.thickness = arr[:, 2]  # in A

    def plot(self):
        """ """

        subplot_rate = figure(
            plot_width=1000,
            plot_height=700,
            x_axis_label="Time / s",
            y_axis_label="Rate / A/s",
            sizing_mode="scale_width",
            tools="reset, save, wheel_zoom, pan, box_zoom, hover, crosshair",
            active_drag="box_zoom",
            active_scroll="wheel_zoom",
            active_inspect="hover",
        )
        subplot_rate.toolbar.logo = None
        subplot_rate.background_fill_alpha = 0
        # plot.circle(x, y, size=2)
        subplot_rate.line(self.time, self.rate, line_width=2)
        subplot_rate.toolbar.active_scroll = "auto"

        subplot_thick = figure(
            plot_width=1000,
            plot_height=700,
            x_axis_label="Time / s",
            y_axis_label="Thickness / A",
            sizing_mode="scale_width",
            tools="reset, save, wheel_zoom, pan, box_zoom, hover, crosshair",
            active_drag="box_zoom",
            active_scroll="wheel_zoom",
            active_inspect="hover",
        )
        subplot_thick.toolbar.logo = None
        subplot_thick.background_fill_alpha = 0
        # plot.circle(x, y, size=2)
        subplot_thick.line(
            self.time, self.thickness, line_color="seagreen", line_width=2
        )
        subplot_thick.toolbar.active_scroll = "auto"

        plot = row(subplot_rate, subplot_thick)

        self.script, self.div = components(plot, wrap_script=True)
