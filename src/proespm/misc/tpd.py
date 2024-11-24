from datetime import datetime
import itertools
import os
from typing import Self
from bokeh.palettes import Category10_10
import numpy as np
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.models import LinearAxis, Range1d
from numpy.typing import NDArray

from proespm.fileinfo import Fileinfo
from proespm.labjournal import Labjournal


class Tpd:
    def __init__(self, filepath: str) -> None:
        self.ident = "TPD"
        self.fileinfo = Fileinfo(filepath)
        self.datetime = datetime.fromtimestamp(os.path.getmtime(filepath))
        self.m_id = self.fileinfo.filename

        self.script: str | None = None
        self.div: str | None = None

        self.data = self.get_data()

        self.colors = itertools.cycle(Category10_10)

        self.script, self.div = None, None
        self.labjournal_data = None

    def get_data(self) -> dict[str, NDArray[np.float64]]:
        with open(self.fileinfo.filepath, "r") as f:
            header = f.readline()
            _ = f.seek(0)
            numeric_data = np.loadtxt(f, skiprows=1).T

        header_entries = [
            entry.split("_")[0]
            .replace("ti", "Time")
            .replace("Te", "Temperature")
            for entry in header.split()
            if "Q" not in entry
        ]

        return {k: v for k, v in zip(header_entries, numeric_data)}

    def plot(self) -> None:
        """Creates an interactive plot of the data"""
        time_data: NDArray[np.float64] = self.data.pop("Time")
        temperature_data: NDArray[np.float64] = self.data.pop("Temperature")
        y_min = np.inf
        y_max = 0
        for arr in self.data.values():
            min: np.float64 = arr.min()
            max: np.float64 = arr.max()
            if min < y_min:
                y_min = min - 0.1 * max
            if max > y_max:
                y_max = max

        y_min -= 0.1 * y_max
        y_max += 0.1 * y_max


        plot = figure(
            width=1000,
            height=540,
            x_axis_label="Time / s",
            y_axis_label="Ion Current / A",
            y_range=(y_min, y_max),
            # x_range=x_range,
            sizing_mode="scale_width",
            tools="reset, save, wheel_zoom, pan, box_zoom, hover, crosshair",
            active_drag="box_zoom",
            active_scroll="wheel_zoom",
            active_inspect="hover",
        )
        plot.toolbar.logo = None  # pyright: ignore[reportAttributeAccessIssue]
        plot.background_fill_alpha = 0
        plot.toolbar.active_scroll = "auto"  # pyright: ignore[reportAttributeAccessIssue]
        for k, v in self.data.items():
            _ = plot.line(time_data, v, legend_label=k, color=next(self.colors), line_width=2)

        # Second Axis (right) for Temperature
        second_y_range_name = "Temperature"
        plot.extra_y_ranges[second_y_range_name] = Range1d(
            temperature_data.min() - 5, temperature_data.max() + 5
        )
        ax2 = LinearAxis(
            y_range_name=second_y_range_name, axis_label="Temperature / °C"
        )
        plot.add_layout(ax2, "right")
        _ = plot.line(
            time_data,
            temperature_data,
            legend_label="T",
            color=next(self.colors),
            y_range_name=second_y_range_name,
            line_width=2,
        )

        self.script, self.div = components(plot, wrap_script=True)

    def process(self) -> Self:
        self.plot()
        return self

    def set_labjournal_data(self, labjournal: Labjournal) -> None:
        self.labjournal_data = labjournal.extract_metadata_for_m_id(self.m_id)
