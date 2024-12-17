from __future__ import annotations
import re
from datetime import datetime
from typing import Self
import numpy as np
from bokeh.embed import components
from dateutil import parser
from numpy._typing import NDArray
from proespm.ec.ec import EcPlot
from proespm.fileinfo import Fileinfo
from proespm.labjournal import Labjournal


DATETIME_REGEX = re.compile(r"Date and time:,([\d\s:-]+)")


class Lsv:
    """Class for handling PalmSens linear sweep voltammetry files (.csv)
    (testfile: PS241105-13.csv)
    """

    ident = "lsv"


    def __init__(self, filepath: str) -> None:
        self.fileinfo = Fileinfo(filepath)
        self.m_id = self.fileinfo.filename
        self.labjournal_data: dict[str, str] | None = None

        self.datetime: datetime | None = None
        self.read_params()

        self.ec_type: str | None = None

        self.data: list[NDArray[np.float64]] = [self.read_cv_data(filepath)]
        self.script: str | None = None
        self.div: str | None = None

    def read_cv_data(self, filepath: str) -> NDArray[np.float64]:
        return np.genfromtxt(
            filepath,
            delimiter=",",
            skip_header=6,
            skip_footer=1,
            encoding="utf-16",
        )

    def read_params(self) -> None:
        with open(self.fileinfo.filepath, encoding = 'utf-16')  as f:
            content = f.read()
            datetime_match = DATETIME_REGEX.search(content)

            if datetime_match is not None:
                self.datetime = parser.parse(datetime_match.group(1).strip())

    def plot(self):
        plot = EcPlot()
        plot.set_x_axis_label("E [V]")
        plot.set_y_axis_label("I [µA]")

        for i, arr in enumerate(self.data):
            x = arr[:, 0]  # time
            y = arr[:, 1]  # current

            plot.plot_scatter(x, y, legend_label=f"Cycle {i + 1}")

        plot.set_legend_location("bottom_right")
        self.script, self.div = components(plot.fig, wrap_script=True)

    def process(self) -> Self:
        self.plot()
        return self

    def set_labjournal_data(self, labjournal: Labjournal) -> None:
        self.labjournal_data = labjournal.extract_metadata_for_m_id(self.m_id)



