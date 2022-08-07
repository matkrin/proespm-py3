import os
import datetime
import numpy as np
from bokeh.plotting import figure
from bokeh.embed import components


class Aes:
    """"""

    def __init__(self, filepath):
        self.filepath = filepath
        self.basename = os.path.basename(self.filepath)
        self.dirname = os.path.dirname(self.filepath)
        self.filename, self.fileext = os.path.splitext(self.basename)
        self.m_id = self.filename
        self.read_staib_dat(filepath)

    def read_staib_dat(self, filepath):
        """reads the .dat file format of the STAIB CMA"""

        def read_header_line(f):
            """reads one line of the header"""
            return f.readline().split(":")[-1].strip()

        with open(filepath, "r") as f:
            self.version = read_header_line(f)
            self.spectrum_type = read_header_line(f)
            self.technique = read_header_line(f)
            self.source_label = read_header_line(f)
            self.source_energy = float(read_header_line(f))
            self.mode = read_header_line(f)
            self.channels = int(read_header_line(f))
            self.samples = int(read_header_line(f))

            self.e_start = float(read_header_line(f))  # in V
            self.e_stop = float(read_header_line(f))  # in V

            self.stepwidth = float(read_header_line(f))
            self.res_mode = read_header_line(f)
            self.res = float(read_header_line(f))
            self.data_points = int(read_header_line(f))
            self.scan_num = int(read_header_line(f))
            self.dwell_time = int(read_header_line(f))  # in ms
            self.retrace_time = int(read_header_line(f))  # in ms
            self.description_len = read_header_line(f)

            self.datetime = datetime.datetime.strptime(
                f.readline().split("    ")[-1].strip(), "%a %b %d %H:%M:%S %Y"
            )

            self.reserved_1 = read_header_line(f)
            self.reserved_2 = read_header_line(f)
            self.reserved_3 = read_header_line(f)
            self.reserved_4 = read_header_line(f)

            self.data_header = f.readline().strip()  # data in mV

            self.aes_data = np.array([float(x) for x in f.readline().split()])
            for _ in range(self.data_points - 1):
                line = [float(x) for x in f.readline().split()]
                arr_line = np.array(line)
                self.aes_data = np.vstack((self.aes_data, arr_line))

    def plot(self):
        """ """
        x = self.aes_data[:, 0] / 1000
        y = self.aes_data[:, 1]

        plot = figure(
            plot_width=1000,
            plot_height=540,
            x_axis_label="E / eV",
            y_axis_label="Intensity / arb. units",
            x_range=(x[0], x[-1]),
            sizing_mode="scale_width",
            tools="reset, save, wheel_zoom, pan, box_zoom, hover, crosshair",
            active_drag="box_zoom",
            active_scroll="wheel_zoom",
            active_inspect="hover",
        )
        plot.toolbar.logo = None
        plot.background_fill_alpha = 0
        # plot.circle(x, y, size=2)
        plot.line(x, y)
        plot.toolbar.active_scroll = "auto"
        self.script, self.div = components(plot, wrap_script=True)
