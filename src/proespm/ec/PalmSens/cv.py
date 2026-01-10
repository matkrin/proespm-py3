from __future__ import annotations

import re
from datetime import datetime
from typing import Literal, Self, final, override

import numpy as np
from bokeh.embed import components
from dateutil import parser
from numpy._typing import NDArray

from proespm.ec.ec import EcPlot
from proespm.fileinfo import Fileinfo
from proespm.config import Config
from proespm.measurement import Measurement

DATETIME_REGEX = re.compile(r"Date and time measurement:,([\d\s:-]+)")


@final
class CvPalmSens(Measurement):
    """Class for handling PalmSens cyclic voltammetry files (.csv)
    (testfile: PS241105-3.csv)
    """

    ident: Literal["CV_PALMSENS"] = "CV_PALMSENS"

    def __init__(self, filepath: str) -> None:
        self.fileinfo: Fileinfo = Fileinfo(filepath)
        self.m_id: str = self.fileinfo.filename

        self.datetime: datetime | None = None
        self.read_params()

        self.ec_type: str | None = None

        self.data: NDArray[np.float64] = self.read_cv_data(filepath)
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
        with open(self.fileinfo.filepath, encoding="utf-16") as f:
            content = f.read()
            datetime_match = DATETIME_REGEX.search(content)
            if datetime_match is not None:
                self.datetime = parser.parse(datetime_match.group(1).strip())

    def plot(self):
        plot = EcPlot()
        plot.set_x_axis_label("E [V]")
        plot.set_y_axis_label("I [µA]")

        for i in range(0, self.data.shape[1], 2):
            x = self.data[:, i]  # voltage
            y = self.data[:, i + 1]  # current

            plot.plot_scatter(x, y, legend_label=f"Cycle {i // 2 + 1}")

        plot.set_legend_location("bottom_right")
        self.script, self.div = components(plot.fig, wrap_script=True)

    @override
    def process(self, config: Config) -> Self:
        self.plot()
        return self

    @override
    def template_name(self) -> str:
        return "ec4.j2"
