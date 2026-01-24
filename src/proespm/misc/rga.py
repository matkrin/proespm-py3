from dataclasses import dataclass
import itertools
from bokeh.palettes import Category10_10
from bokeh.embed import components
from bokeh.plotting import figure
from proespm.fileinfo import Fileinfo
from typing import Self, final, override, TextIO
from proespm.config import Config
import datetime
import dateutil
from proespm.measurement import Measurement
import numpy as np


@final
class RgaMassScan(Measurement):
    def __init__(self, filepath: str) -> None:
        self.fileinfo = Fileinfo(filepath)

        self.script: str | None = None
        self.div: str | None = None

        with open(filepath, "r") as f:
            self._datetime = dateutil.parser.parse(f.readline())
            self.software = f.readline()

            for _ in range(4):
                _ = next(f)

            self.num_datapoints = f.readline().split(", ")[-1]
            self.units = f.readline().split(", ")[-1]
            self.noise_floor = f.readline().split(", ")[-1]
            self.cem_status = f.readline().split(", ")[-1]
            self.points_per_amu = f.readline().split(", ")[-1]

            _skip_until_two_empty_lines(f)
            self.data = np.genfromtxt(f, delimiter=",", usecols=(0, 1))

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
        _ = plot.line(
            self.data[:, 0],
            self.data[:, 1],
            line_width=2,
        )
        self.script, self.div = components(plot, wrap_script=True)

    @override
    def m_id(self) -> str:
        return self.fileinfo.filename

    @override
    def datetime(self) -> datetime.datetime:
        return self._datetime

    @override
    def process(self, config: Config) -> Self:
        self.plot()
        return self

    @override
    def template_name(self) -> str | None:
        return "tpd.j2"


@dataclass
class RgaChannel:
    channel_num: int
    mass: int
    name: str
    cal_factor: float
    noise_floor: int
    cem_status: bool

    @classmethod
    def from_line(cls, line: str):
        s = [x.strip() for x in line.split(",")]
        return cls(
            channel_num=int(s[0]),
            mass=int(s[1]),
            name=s[2],
            cal_factor=float(s[3]),
            noise_floor=int(s[4]),
            cem_status=True if s[5] == "ON" else False,
        )


@final
class RgaTimeSeries(Measurement):
    def __init__(self, filepath: str) -> None:
        self.fileinfo = Fileinfo(filepath)

        self.colors = itertools.cycle(Category10_10)
        self.script: str | None = None
        self.div: str | None = None

        with open(filepath, "r") as f:
            self._datetime = dateutil.parser.parse(f.readline())
            self.software = f.readline()

            for _ in range(4):
                _ = next(f)

            self.active_channels = f.readline().split(", ")[-1]
            self.units = f.readline().split(", ")[-1]
            self.sample_period = f.readline().split(", ")[-1]

            line = f.readline()
            while "Start time" not in line:
                line = f.readline()

            _ = next(f)
            self.channels = self.read_channels(f)
            self.data = np.genfromtxt(f, delimiter=",")[:, :-1]

    def read_channels(self, file_io: TextIO) -> list[RgaChannel]:
        channels: list[RgaChannel] = []
        while True:
            line = file_io.readline()
            if line.strip() == "":
                break
            channels.append(RgaChannel.from_line(line))

        return channels

    def plot(self) -> None:
        time = self.data[:, 0]
        signals = self.data[:, 1:]

        plot = figure(
            width=1000,
            height=540,
            x_axis_label="Time / s",
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

        for i in range(signals.shape[1]):
            _ = plot.line(
                time,
                signals[:, i],
                line_width=2,
                legend_label=f"{self.channels[i].mass} ({self.channels[i].name})",
                color=next(self.colors),
                alpha=0.8,
            )

        self.script, self.div = components(plot, wrap_script=True)

    @override
    def m_id(self) -> str:
        return self.fileinfo.filename

    @override
    def datetime(self) -> datetime.datetime:
        return self._datetime

    @override
    def process(self, config: Config) -> Self:
        self.plot()
        return self

    @override
    def template_name(self) -> str | None:
        return "tpd.j2"


def _skip_until_two_empty_lines(f: TextIO):
    empty_count = 0
    for line in f:
        if line.strip() == "":
            empty_count += 1
            if empty_count == 2:
                return
        else:
            empty_count = 0
