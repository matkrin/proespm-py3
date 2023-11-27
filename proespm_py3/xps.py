import numpy as np
import os
import datetime
from bokeh.plotting import figure
from bokeh.embed import components


class XpsEis:
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.basename = os.path.basename(filepath)
        self.filename, self.fileext = os.path.splitext(self.basename)
        self.datetime = datetime.datetime.utcfromtimestamp(
            os.path.getmtime(filepath)
        )
        self.data = self.read_xps_eis_txt(filepath)

    def read_xps_eis_txt(self, filepath):
        """Reads the data of a .txt file from Omicron EIS software"""
        with open(filepath) as f:
            scan_num = f.read().count("Region")
            f.seek(0)

            data = []
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
                        self.filepath,
                        xps_data,
                        scan_dict["Region"],
                        scan_dict["Start"],
                        scan_dict["End"],
                        scan_dict["Step"],
                        scan_dict["Sweeps"],
                        scan_dict["Dwell"],
                        scan_dict["CAE/CRR"],
                    )
                )
        return data


class XpsScan:
    def __init__(
        self,
        filepath,
        xps_data,
        scan_number,
        start,
        end,
        step,
        sweeps,
        dwell,
        e_pass,
    ):
        self.filepath = filepath
        self.basename = os.path.basename(filepath)
        self.filename, self.fileext = os.path.splitext(self.basename)
        self.datetime = datetime.datetime.utcfromtimestamp(
            os.path.getmtime(filepath)
        )

        self.xps_data = xps_data
        self.scan_number = scan_number
        self.start = start
        self.end = end
        self.step = step
        self.sweeps = sweeps
        self.dwell = dwell
        self.e_pass = e_pass

        self.m_id = f"{self.filename}_{self.scan_number}"
        self.sheet_id: str | None = None

    def plot(self):
        """ """
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
        plot.toolbar.logo = None
        plot.background_fill_alpha = 0
        plot.line(x, y)
        plot.toolbar.active_scroll = "auto"
        self.script, self.div = components(plot, wrap_script=True)
