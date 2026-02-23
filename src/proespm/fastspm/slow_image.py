import base64
from datetime import datetime, timezone
from pathlib import Path
from typing import Self, final, override
import io

import h5py

from proespm.config import Config
from proespm.fastspm.fastspm import read_corresponding_image
from proespm.fileinfo import Fileinfo
from proespm.measurement import Measurement


@final
class SlowImage(Measurement):
    """Class for handling .h5 files of slow image (SI) measurements.

    Args:
        filepath (str): Full path to the .h5 file
    """

    op_mode = "SI"

    def __init__(self, filepath: str) -> None:
        self.fileinfo = Fileinfo(filepath)

        self.img_uri: str | None = None
        self.slide_num: int | None = None

        with h5py.File(filepath, "r") as f:
            self.attributes = dict(f.attrs)

            # def show_attrs(name, obj):
            #     print(f"= {obj} =")
            #     if obj.attrs:
            #         print(f"  [{name}]")
            #         for k, v in obj.attrs.items():
            #             print(f"    {k} -> {v}")

            # f.visititems(show_attrs)

        # for k, v in self.attributes.items():
        #     print(f"{k}->{v}".encode("utf8", "backslashreplace"))

        self.aux_1 = float(self.attributes.get("Aux1.Value","0"))*float(self.attributes.get("Aux1.ConversionFactor","0")) * (2 * float(self.attributes.get("Aux1.InvertSignalIn","0")) - 1)
        self.aux_1_unit = self.attributes.get("Aux1.Unit","")
        self.aux_1_label = self.attributes.get("Aux1.Label","")

        self.aux_2 = float(self.attributes.get("Aux2.Value","0"))*float(self.attributes.get("Aux2.ConversionFactor","0")) * (2 * float(self.attributes.get("Aux2.InvertSignalIn","0")) - 1)
        self.aux_2_unit = self.attributes.get("Aux2.Unit","")
        self.aux_2_label = self.attributes.get("Aux2.Label","")

        self.z_in_convfact = float(self.attributes.get("Z_In.ConversionFactor","nan"))
        self.z_in_offset = float(self.attributes.get("Z_In.Offset","nan"))
        self.z_in_unit = self.attributes.get("Z_In.Unit","")

        self.temp_start = self.attributes.get("ExperimentInfo.TemperatureStart","nan")
        self.temp_end = self.attributes.get("ExperimentInfo.TemperatureEnd","nan")
        self.temp_unit = self.attributes.get("ExperimentInfo.Temperature.Unit","nan")

        self.time_per_pixel = self.attributes.get("PI.ControlTimeStep","")
        self.time_per_pixel_unit = self.attributes.get("PI.ControlTimeStep.Unit","")

    @override
    def m_id(self) -> str:
        return self.fileinfo.filename

    @override
    def datetime(self) -> datetime:
        time_start = self.attributes["ExperimentInfo.TimeStart"]  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
        assert isinstance(time_start, str)  # Type assertion

        return (
            datetime.fromisoformat(time_start)
            .astimezone(timezone.utc)
            .replace(tzinfo=None)
        )

    @override
    def process(self, config: Config) -> Self:
        self.img_uri = read_corresponding_image(self.fileinfo.filepath, True)
        return self

    @override
    def template_name(self) -> str:
        return "fastspm.j2"
