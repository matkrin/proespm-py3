import json
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Hashable, Literal, Self, final

import numpy as np
from bokeh.embed import components
from numpy.typing import NDArray

from proespm.ec.ec import EcPlot
from proespm.fileinfo import Fileinfo
from proespm.config import Config


class PalmSensType(Enum):
    EIS = "Impedance Spectroscopy"
    LSV = "Linear Sweep Voltammetry"
    CV = "Cyclic Voltammetry"
    CA = "Chronoamperometry"
    CP = "Chronopotentiometry"


@final
class PalmSensSession:
    ident: Literal["PS_SESSION"] = "PS_SESSION"

    def __init__(self, filepath: str) -> None:
        self.fileinfo: Fileinfo = Fileinfo(filepath)
        self.m_id: str = self.fileinfo.filename
        self.script: str | None = None
        self.div: str | None = None

        with open(filepath, "r", encoding="utf-16") as f:
            content = f.read()
            self.parsed: dict[Hashable, Any] = json.loads(content[:-1])  # pyright: ignore[reportExplicitAny]

        title: str = self.parsed["Measurements"][0]["Title"]
        self.session_type: PalmSensType = PalmSensType(title)

        timestamp_in_10e7: int = self.parsed["Measurements"][0]["TimeStamp"]
        base_date = datetime(1, 1, 1)
        timestamp_in_seconds = timestamp_in_10e7 * 1e-7
        self.datetime: datetime = base_date + timedelta(
            seconds=timestamp_in_seconds
        )

        self.file_metadata: str = self.parsed["MethodForMeasurement"]
        self.data: NDArray[np.float64] = self._get_data()

    def _get_data(self) -> NDArray[np.float64]:
        dataset_values = self.parsed["Measurements"][0]["DataSet"]["Values"]

        match self.session_type:
            case PalmSensType.EIS:
                z_re = [x["V"] for x in dataset_values[4]["DataValues"]]
                z_im = [x["V"] for x in dataset_values[5]["DataValues"]]
                return np.array([z_re, z_im]).T

            case PalmSensType.CV:
                data: list[list[float]] = []
                for values_arr in dataset_values:
                    values: list[float] = []
                    for v in values_arr["DataValues"]:
                        values.append(v["V"])

                    data.append(values)

                return np.array(data).T

            case PalmSensType.LSV | PalmSensType.CA | PalmSensType.CP:
                time = [x["V"] for x in dataset_values[0]["DataValues"]]
                potential = [x["V"] for x in dataset_values[1]["DataValues"]]
                current = [x["V"] for x in dataset_values[2]["DataValues"]]
                charge = [x["V"] for x in dataset_values[3]["DataValues"]]

                return np.array([time, potential, current, charge]).T

    def plot(self):
        plot = EcPlot()

        match self.session_type:
            case PalmSensType.EIS:
                plot.set_x_axis_label("Z' [Ohm]")
                plot.set_y_axis_label("Z'' [Ohm]")

                x = self.data[:, 0]  # Z_Re
                y = self.data[:, 1]  # Z_Im

                plot.plot_scatter(x, y)
                plot.show_legend(False)

            case PalmSensType.CV:
                plot.set_x_axis_label("E [V]")
                plot.set_y_axis_label("I [µA]")
                for i in range(1, self.data.shape[1] - 1, 3):
                    x = self.data[:, i]  # voltage
                    y = self.data[:, i + 1]  # current

                    plot.plot_scatter(x, y, legend_label=f"Cycle {i // 3 + 1}")

                plot.set_legend_location("bottom_right")

            case PalmSensType.LSV:
                plot.set_x_axis_label("E [V]")
                plot.set_y_axis_label("I [µA]")

                x = self.data[:, 1]  # voltage
                y = self.data[:, 2]  # current

                plot.plot_scatter(x, y)
                plot.show_legend(False)

            case PalmSensType.CA:
                plot.set_x_axis_label("t [s]")
                plot.set_y_axis_label("I [µA]")

                time = self.data[:, 0]
                potential = self.data[:, 1]
                current = self.data[:, 2]

                potential_min: float = potential.min() * 0.95
                potential_max: float = potential.max() * 1.05

                current_min: float = current.min() * 1.05
                current_max: float = current.max() * 0.8

                plot.set_y_range(current_min, current_max)
                plot.add_second_axis(
                    "voltage", potential_min, potential_max, axis_label="U [V]"
                )
                plot.plot_scatter(time, current, legend_label="I")
                plot.plot_second_axis(time, potential, legend_label="U")

            case PalmSensType.CP:
                plot.set_x_axis_label("t [s]")
                plot.set_y_axis_label("E [V]")

                x = self.data[:, 0]  # time
                y = self.data[:, 1]  # voltage

                plot.plot_scatter(x, y)
                plot.show_legend(False)

        self.script, self.div = components(plot.fig, wrap_script=True)

    def process(self, _config: Config) -> Self:
        self.plot()
        return self
