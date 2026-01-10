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

DATETIME_REGEX = re.compile(
    r"Date and time:,(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})"
)


@final
class EisPalmSens(Measurement):
    """Class for handling PalmSens impedence spectroscopy files (.csv)
    (testfile: PS241105-14.csv)
    """

    ident: Literal["EIS_PALMSENS"] = "EIS_PALMSENS"

    def __init__(self, filepath: str) -> None:
        self.fileinfo: Fileinfo = Fileinfo(filepath)

        self._datetime: datetime | None = None
        self.read_params()

        self.ec_type: str | None = None

        self.data: NDArray[np.float64] = self.read_cv_data(filepath)
        self.script: str | None = None
        self.div: str | None = None

    def read_cv_data(self, filepath: str) -> NDArray[np.float64]:
        return np.genfromtxt(
            filepath,
            usecols=[4, 5],
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
                self._datetime = parser.parse(datetime_match.group(1).strip())

    def plot(self):
        plot = EcPlot()
        plot.set_x_axis_label("Z' [Ohm]")
        plot.set_y_axis_label("Z'' [Ohm]")

        x = self.data[:, 0]  # Z'
        y = self.data[:, 1]  # Z''

        plot.plot_scatter(x, y)
        plot.show_legend(False)

        self.script, self.div = components(plot.fig, wrap_script=True)

    @override
    def m_id(self) -> str:
        return self.fileinfo.filename

    @override
    def datetime(self) -> datetime:
        assert self._datetime is not None  # Type assertion
        return self._datetime

    @override
    def process(self, config: Config) -> Self:
        self.plot()
        return self

    @override
    def template_name(self) -> str:
        return "ec4.j2"
