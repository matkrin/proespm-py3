from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Hashable, Literal, Self, final

import numpy as np
from bokeh.embed import components
from dateutil import parser
from numpy._typing import NDArray

from proespm.ec.ec import EcPlot
from proespm.ec.PalmSens import PARAM_MAP
from proespm.fileinfo import Fileinfo
from proespm.config import Config
from proespm.labjournal import Labjournal

DATETIME_REGEX = re.compile(
    r"Date and time:,(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})"
)


@final
class EisPalmSens:
    """Class for handling PalmSens impedence spectroscopy files (.csv)
    (testfile: PS241105-14.csv)
    """

    ident: Literal["EIS_PALMSENS"] = "EIS_PALMSENS"

    def __init__(self, filepath: str) -> None:
        self.fileinfo: Fileinfo = Fileinfo(filepath)
        self.m_id: str = self.fileinfo.filename
        self.sheet_id: str | None = None
        self.labjournal_data: dict[Hashable, Any] | None = None

        self.datetime: datetime | None = None
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
                self.datetime = parser.parse(datetime_match.group(1).strip())

    def plot(self):
        plot = EcPlot()
        plot.set_x_axis_label("Z' [Ohm]")
        plot.set_y_axis_label("Z'' [Ohm]")

        x = self.data[:, 0]  # Z'
        y = self.data[:, 1]  # Z''

        plot.plot_scatter(x, y)
        plot.show_legend(False)

        self.script, self.div = components(plot.fig, wrap_script=True)

    def process(self, _config: Config) -> Self:
        self.plot()
        return self

    def set_labjournal_data(self, labjournal: Labjournal) -> None:
        metadata = labjournal.extract_metadata_for_m_id(self.m_id)
        if metadata is not None:
            self.sheet_id, self.labjournal_data = metadata
            self.labjournal_data = {
                PARAM_MAP.get(k, k): v for k, v in self.labjournal_data.items()
            }
