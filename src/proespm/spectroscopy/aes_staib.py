from typing import Self, TextIO, final, override

import numpy as np
from bokeh.embed import components
from bokeh.plotting import figure
from dateutil import parser
from numpy._typing import NDArray
from proespm.config import Config
from proespm.measurement import Measurement
from vamas.vamas import Vamas

from proespm.fileinfo import Fileinfo


@final
class AesStaib(Measurement):
    """Class for handling files from Staib DESA

    Args:
        filepath (str): Path to .dat or .vms file
    """

    def __init__(self, filepath: str) -> None:
        self.ident = "AES"
        self.fileinfo = Fileinfo(filepath)
        self.m_id = self.fileinfo.filename

        self.datetime = None
        self.mode = None
        self.dwell_time = None
        self.scan_num = None

        self.e_start = None
        self.e_stop = None
        self.stepwidth = None

        self.retrace_time = None
        self.res_mode = None
        self.res = None
        self.aes_data = None  # pyright: ignore[reportAttributeAccessIssue]
        self.script, self.div = None, None

        if self.fileinfo.fileext == ".vms":
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
            f"{data.year}-{data.month}-{data.day} {data.hour}:{data.minute}:{data.second}"
        )
        self.mode = data.signal_mode
        self.dwell_time = data.signal_collection_time
        self.scan_num = data.num_scans_to_compile_block

        self.e_start = data.x_start
        self.e_stop = (
            data.x_step * data.num_y_values + data.x_start
        ) - data.x_step
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
            (data.x_step * data.num_y_values + data.x_start) - data.x_step,
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
            _version = read_header_line(f)
            _spectrum_type = read_header_line(f)
            _technique = read_header_line(f)
            _source_label = read_header_line(f)
            _source_energy = float(read_header_line(f))
            self.mode = read_header_line(f)
            _channels = int(read_header_line(f))
            _samples = int(read_header_line(f))

            self.e_start = float(read_header_line(f))  # in V
            self.e_stop = float(read_header_line(f))  # in V

            self.stepwidth = float(read_header_line(f))
            self.res_mode = read_header_line(f)
            self.res = float(read_header_line(f))
            _data_points = int(read_header_line(f))
            self.scan_num = int(read_header_line(f))
            self.dwell_time = int(read_header_line(f))  # in ms
            self.retrace_time = int(read_header_line(f))  # in ms
            _description_len = read_header_line(f)

            self.datetime = parser.parse(f.readline().split("    ")[-1].strip())

            _reserved_1 = read_header_line(f)
            _reserved_2 = read_header_line(f)
            _reserved_3 = read_header_line(f)
            _reserved_4 = read_header_line(f)

            _data_header = f.readline().strip()  # data in mV

            self.aes_data = np.array([float(x) for x in f.readline().split()])
            for _ in range(_data_points - 1):
                line = [float(x) for x in f.readline().split()]
                arr_line = np.array(line)
                self.aes_data: NDArray[np.float32] = np.vstack(
                    (self.aes_data, arr_line)
                )

            for i, x in enumerate(self.aes_data[:, 0]):  # pyright: ignore[reportAny]
                self.aes_data[i, 0] = x / 1000

    def plot(self) -> None:
        """Creates a plot for AES data

        The plot gets assigned to the attributes script and div which contains
        html and js that is used in the corresponding jinja template

        """
        x = self.aes_data[:, 0]
        y = self.aes_data[:, 1]

        plot = figure(
            width=1000,
            height=540,
            x_axis_label="E / eV",
            y_axis_label="dN / dE [arb. units]",
            x_range=(x[0], x[-1]),
            sizing_mode="scale_width",
            tools="reset, save, wheel_zoom, pan, box_zoom, hover, crosshair",
            active_drag="box_zoom",
            active_scroll="wheel_zoom",
            active_inspect="hover",
        )
        plot.toolbar.logo = None  # pyright: ignore[reportAttributeAccessIssue]
        plot.background_fill_alpha = 0
        # plot.circle(x, y, size=2)
        _ = plot.line(x, y)
        plot.toolbar.active_scroll = "auto"  # pyright: ignore[reportAttributeAccessIssue]
        self.script, self.div = components(plot, wrap_script=True)

    @override
    def process(self, config: Config) -> Self:
        self.plot()
        return self

    @override
    def template_name(self) -> str:
        return "aes.j2"
