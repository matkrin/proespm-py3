import itertools

from bokeh.plotting import figure
from bokeh.models import LinearAxis, Range1d
from bokeh.palettes import Category10_10
import numpy as np
from numpy._typing import NDArray


class EcPlot:
    """A electrochemistry plot"""

    def __init__(self):
        self.fig = figure(
            width=1000,
            height=540,
            sizing_mode="scale_width",
            tools="reset, save, wheel_zoom, pan, box_zoom, hover, crosshair",
            active_drag="box_zoom",
            active_scroll="wheel_zoom",
            active_inspect="hover",
        )
        self.fig.toolbar.logo = None  # pyright: ignore[reportAttributeAccessIssue]
        self.fig.background_fill_alpha = 0
        self.fig.toolbar.active_scroll = "auto"  # pyright: ignore[reportAttributeAccessIssue]
        self.colors = itertools.cycle(Category10_10)
        self.y_range_name = ""

    def set_x_axis_label(self, label_text: str) -> None:
        self.fig.xaxis.axis_label = label_text

    def set_y_axis_label(self, label_text: str) -> None:
        self.fig.yaxis.axis_label = label_text

    def set_y_range(self, min: float, max: float) -> None:
        self.fig.y_range = Range1d(min, max)

    def set_legend_location(self, location: str) -> None:
        self.fig.legend.location = location

    def plot_scatter(
        self,
        x_values: NDArray[np.int32 | np.float64],
        y_values: NDArray[np.float32 | np.float64],
        legend_label: str = "",
    ) -> None:
        _ = self.fig.scatter(
            x_values,
            y_values,
            size=2,
            legend_label=legend_label,
            color=next(self.colors),
        )

    def plot_line(
        self,
        x_values: NDArray[np.float32 | np.float64],
        y_values: NDArray[np.float32 | np.float64],
    ) -> None:
        _ = self.fig.line(x_values, y_values)

    def add_second_axis(
        self,
        y_range_name: str,
        range_min: float,
        range_max: float,
        axis_label: str,
    ) -> None:
        self.y_range_name = y_range_name
        self.fig.extra_y_ranges[y_range_name] = Range1d(range_min, range_max)  # pyright: ignore[reportIndexIssue]
        ax2 = LinearAxis(y_range_name=y_range_name, axis_label=axis_label)
        self.fig.add_layout(ax2, "right")

    def plot_second_axis(
        self,
        x_values: NDArray[np.float32 | np.float64],
        y_values: NDArray[np.float32 | np.float64],
        legend_label: str = "",
    ):
        _ = self.fig.scatter(
            x_values,
            y_values,
            size=2,
            legend_label=legend_label,
            color=next(self.colors),
            y_range_name=self.y_range_name,
        )

    def show_legend(self, show: bool):
        self.fig.legend.visible = show
