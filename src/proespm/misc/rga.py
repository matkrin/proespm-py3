from bokeh.embed import components
from bokeh.plotting import figure
from proespm.fileinfo import Fileinfo
from typing import Self, final
from proespm.config import Config
import datetime
import dateutil
from proespm.measurement import Measurement
import numpy as np


@final
class Rga(Measurement):
    def __init__(self, filepath: str) -> None:
        self.fileinfo = Fileinfo(filepath)

        self.script: str | None = None
        self.div: str | None = None
        
        with open(filepath, "r") as f:
            self._datetime = dateutil.parser.parse(f.readline())
            self.software = f.readline()

            for _ in range(4):
                next(f)

            self.num_datapoints = f.readline().split(", ")[-1]
            self.units = f.readline().split(", ")[-1]
            self.noise_floor = f.readline().split(", ")[-1]
            self.cem_status = f.readline().split(", ")[-1]
            self.points_per_amu = f.readline().split(", ")[-1]

            self.data = np.genfromtxt(f, skip_header=11, delimiter=',', usecols=(0,1))

    def plot(self) -> None:
        plot = figure(
            width=1000,
            height=540,
            x_axis_label="Mass / amu",
            y_axis_label="Ion Current / A",
            sizing_mode="scale_width",
            tools="reset, save, wheel_zoom, pan, box_zoom, hover, crosshair",
            active_drag="box_zoom",
            active_scroll="wheel_zoom",
            active_inspect="hover",
        )
        plot.toolbar.logo = None  # pyright: ignore[reportAttributeAccessIssue]
        plot.background_fill_alpha = 0
        plot.toolbar.active_scroll = "auto"  # pyright: ignore[reportAttributeAccessIssue]
        plot.line(
            self.data[:,0],
            self.data[:,1],
            line_width=2,
        )
        self.script, self.div = components(plot, wrap_script=True)

    def m_id(self) -> str:
        return self.fileinfo.filename

    def datetime(self) -> datetime.datetime:
        return self._datetime

    def process(self, config: Config) -> Self:
        self.plot()
        return self

    def template_name(self) -> str | None:
        return "tpd.j2"


# rga = Rga("/Users/matthias/Developer/proespm-py3/tests/testdata/rga-test.txt")
