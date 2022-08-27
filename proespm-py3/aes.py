from typing import TextIO
import os
from dateutil import parser
import datetime
import numpy as np
from bokeh.plotting import figure
from bokeh.embed import components
from vamas import Vamas


class Aes:
    """Class for handling files from Staib DESA

    Args:
        filepath (str): Path to .dat or .vms file

    """

    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.basename = os.path.basename(self.filepath)
        self.dirname = os.path.dirname(self.filepath)
        self.filename, self.fileext = os.path.splitext(self.basename)
        self.m_id = self.filename

        if self.fileext == ".vms":
            self.read_staib_vamas(filepath)
        else:
            self.read_staib_dat(filepath)

    def read_staib_vamas(self, filepath: str) -> None:
        """Uses vamas library to read AES Staib .vms files

        Args:
            filepath (str): Path to the .vms file

        """
        vms = Vamas(filepath)
        # AES Staib vms always contains only one block
        data = vms.blocks[0]
        self.datetime = parser.parse(
            f"{data.year}-{data.month}-{data.day}            "
            f" {data.hour}:{data.minute}:{data.second}"
        )
        self.mode = data.signal_mode
        self.dwell_time = data.signal_collection_time
        self.scan_num = data.num_scans_to_compile_block

        self.e_start = data.x_start
        self.e_stop = data.x_step * data.num_y_values
        self.stepwidth = data.x_step

        for i in data.additional_numerical_params:
            if i.label == "BKSrettime":
                self.retrace_time = i.value
            elif i.label == "BKSresomode":
                self.res_mode = i.value
            elif i.label == "BKSresol":
                self.res = i.value

        x_values = np.linspace(
            data.x_start,
            (data.x_step * data.num_y_values + data.x_start)-data.x_step,
            num=data.num_y_values,
        )
        y_values = np.array(data.corresponding_variables[0].y_values)
        self.aes_data = np.column_stack((x_values, y_values))

    def read_staib_dat(self, filepath: str) -> None:
        """Reads the .dat file format of the STAIB CMA

        Args:
            filepath (str): Path to the .dat file

        """

        def read_header_line(f: TextIO) -> str:
            """Reads one line of the header

            Args:
                f (TextIO): Filehander of context manager that opens
                    the .dat file

            Returns:
                The last value of the ':'-splitted textline

            """
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

            for i, x in enumerate(self.aes_data[:, 0]):
                self.aes_data[i, 0] = x / 1000

    def plot(self) -> None:
        """Creates a plot for AES data

        The plot gets assigned to the attributes script and div which contains
        html and js that is used in the corresponding jinja template

        """
        x = self.aes_data[:, 0]
        y = self.aes_data[:, 1]

        plot = figure(
            plot_width=1000,
            plot_height=540,
            x_axis_label="E / eV",
            y_axis_label="dN / dE [arb. units]",
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
