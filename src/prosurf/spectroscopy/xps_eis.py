from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Self

import numpy as np
from bokeh.embed import components
from bokeh.plotting import figure
from numpy._typing import NDArray

from prosurf.fileinfo import Fileinfo
from prosurf.labjournal import Labjournal


class XpsEis:
    """Class handling Omicron EIS XPS files (.txt)"""

    def __init__(self, filepath: str) -> None:
        self.ident = "XPS"
        self.fileinfo = Fileinfo(filepath)
        self.datetime = datetime.fromtimestamp(os.path.getmtime(filepath))
        self.data = self.read_xps_eis_txt(filepath)
        self.m_id = self.fileinfo.basename

    def read_xps_eis_txt(self, filepath: str) -> list[XpsScan]:
        """Reads the data of a .txt file from Omicron EIS software"""
        with open(filepath) as f:
            scan_num = f.read().count("Region")
            _ = f.seek(0)

            data: list[XpsScan] = []
            for _ in range(scan_num):
                scan_dict = dict(xps="vtstm")
                line1 = f.readline().split("\t")
                line1 = [x.rstrip("\n") for x in line1]
                line2 = f.readline().split("\t")
                line2 = [x.rstrip("\n") for x in line2]

                scan_dict.update(dict(zip(line1, line2)))

                line3 = f.readline().split("\t")
                line3 = [x.rstrip("\n") for x in line3]
                line4 = f.readline().split("\t")
                line4 = [x.rstrip("\n") for x in line4]

                scan_dict.update(dict(zip(line3, line4)))

                data_header = f.readline().split("\t")
                data_header = [x.rstrip("\n") for x in data_header]

                start = float(scan_dict["Start"])
                end = float(scan_dict["End"])
                step = float(scan_dict["Step"])

                num_lines = int(abs(start - end) / step)

                xps_data = np.array(
                    [float(x) for x in f.readline().split("\t")]
                )
                for _ in range(num_lines):
                    line = [float(x) for x in f.readline().split("\t")]
                    arr_line = np.array(line)
                    xps_data = np.vstack((xps_data, arr_line))

                data.append(
                    XpsScan(
                        filepath=self.fileinfo.filepath,
                        xps_data=xps_data,
                        scan_number=int(scan_dict["Region"]),
                        start=start,
                        end=end,
                        step=step,
                        sweeps=int(scan_dict["Sweeps"]),
                        dwell=float(scan_dict["Dwell"]),
                        e_pass=float(scan_dict["CAE/CRR"]),
                    )
                )
        return data

    def process(self) -> Self:
        for xps_scan in self.data:
            xps_scan.plot()
        return self

    def set_labjournal_data(self, labjournal: Labjournal) -> None:
        for xps_scan in self.data:
            xps_scan.labjournal_data = labjournal.extract_metadata_for_m_id(
                xps_scan.m_id
            )


class XpsScan:
    """Class handling a single XPS scan in an Omicron EIS data file (.txt)"""

    def __init__(
        self,
        filepath: str,
        xps_data: NDArray[Any],
        scan_number: int,
        start: float,
        end: float,
        step: float,
        sweeps: int,
        dwell: float,
        e_pass: float,
    ) -> None:
        self.filepath = filepath
        self.basename = os.path.basename(filepath)
        self.filename, self.fileext = os.path.splitext(self.basename)
        self.datetime = datetime.fromtimestamp(os.path.getmtime(filepath))
        self.xps_data = xps_data
        self.scan_number = scan_number
        self.start = start
        self.end = end
        self.step = step
        self.sweeps = sweeps
        self.dwell = dwell
        self.e_pass = e_pass

        self.m_id = f"{self.filename}_{self.scan_number}"
        self.labjournal_data: dict[str, str] | None = None

        self.script = None
        self.div = None

    def plot(self) -> None:
        """Creates an interactive plot of the data"""
        x = self.xps_data[:, 0]
        y = self.xps_data[:, 1]

        x_range = (x[-1], x[0])

        plot = figure(
            width=1000,
            height=540,
            x_axis_label="E_b / eV",
            y_axis_label="Intensity / arb. units",
            x_range=x_range,
            sizing_mode="scale_width",
            tools="reset, save, wheel_zoom, pan, box_zoom, hover, crosshair",
            active_drag="box_zoom",
            active_scroll="wheel_zoom",
            active_inspect="hover",
        )
        plot.toolbar.logo = None  # pyright: ignore[reportAttributeAccessIssue]
        plot.background_fill_alpha = 0
        _ = plot.line(x, y)
        plot.toolbar.active_scroll = "auto"  # pyright: ignore[reportAttributeAccessIssue]
        self.script, self.div = components(plot, wrap_script=True)
