import json
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Hashable, Self, cast, final, override

import numpy as np
from bokeh.embed import components
from numpy.typing import NDArray

from proespm.config import Config
from proespm.ec.ec import EcPlot
from proespm.fileinfo import Fileinfo
from proespm.measurement import Measurement


class PalmSensType(Enum):
    EIS = "Impedance Spectroscopy"
    LSV = "Linear Sweep Voltammetry"
    CV = "Cyclic Voltammetry"
    CA = "Chronoamperometry"
    CP = "Chronopotentiometry"


@final
class PalmSensSession(Measurement):
    controller = "PalmSens"

    def __init__(self, filepath: str) -> None:
        self.fileinfo: Fileinfo = Fileinfo(filepath)
        self.script: str | None = None
        self.div: str | None = None

        with open(filepath, "r", encoding="utf-16") as f:
            content = f.read()
            self.parsed: dict[Hashable, Any] = json.loads(content[:-1])  # pyright: ignore[reportExplicitAny]

        title = cast(str, self.parsed["Measurements"][0]["Title"])
        self.session_type: PalmSensType = PalmSensType(title)
        self.ec_type = self.session_type.value

        timestamp_in_10e7: int = cast(
            int, self.parsed["Measurements"][0]["TimeStamp"]
        )
        base_date = datetime(1, 1, 1)
        timestamp_in_seconds = timestamp_in_10e7 * 1e-7
        self._datetime: datetime = base_date + timedelta(
            seconds=timestamp_in_seconds
        )

        self.file_metadata: str = self.parsed["MethodForMeasurement"]
        self.data: NDArray[np.float64] = self._get_data()

    def _get_data(self) -> NDArray[np.float64]:
        dataset_values = self.parsed["Measurements"][0]["DataSet"]["Values"]  # pyright: ignore[reportAny]

        match self.session_type:
            case PalmSensType.EIS:
                z_re = [x["V"] for x in dataset_values[4]["DataValues"]]  # pyright: ignore[reportAny]
                z_im = [x["V"] for x in dataset_values[5]["DataValues"]]  # pyright: ignore[reportAny]
                return np.array([z_re, z_im]).T

            case PalmSensType.CV:
                data: list[list[float]] = []
                for values_arr in dataset_values:  # pyright: ignore[reportAny]
                    values: list[float] = []
                    for v in values_arr["DataValues"]:  # pyright: ignore[reportAny]
                        values.append(v["V"])  # pyright: ignore[reportAny]

                    data.append(values)

                return np.array(data).T

            case PalmSensType.LSV | PalmSensType.CA | PalmSensType.CP:
                time = [x["V"] for x in dataset_values[0]["DataValues"]]  # pyright: ignore[reportAny]
                potential = [x["V"] for x in dataset_values[1]["DataValues"]]  # pyright: ignore[reportAny]
                current = [x["V"] for x in dataset_values[2]["DataValues"]]  # pyright: ignore[reportAny]
                charge = [x["V"] for x in dataset_values[3]["DataValues"]]  # pyright: ignore[reportAny]

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

                potential_min = cast(float, potential.min() * 0.95)
                potential_max = cast(float, potential.max() * 1.05)

                current_min = cast(float, current.min() * 1.05)
                current_max = cast(float, current.max() * 0.8)

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

    @override
    def m_id(self) -> str:
        return self.fileinfo.filename

    @override
    def datetime(self) -> datetime:
        return self._datetime

    @override
    def process(self, config: Config) -> Self:
        self.plot()
        return self

    @override
    def template_name(self) -> str:
        return "ec4.j2"
