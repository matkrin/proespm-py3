from datetime import datetime, timezone
from typing import Self, final, override

import h5py

from proespm.config import Config
from proespm.fastspm.fastspm import read_corresponding_image
from proespm.fileinfo import Fileinfo
from proespm.fastspm.fastspm import FastSPMMeasurement


@final
class ErrorTopography(FastSPMMeasurement):
    """Class for handling .h5 files of error topography (ET) measurements.

    Args:
        filepath (str): Full path to the .h5 file
    """

    op_mode = "ET"

    def __init__(self, filepath: str) -> None:
        self.fileinfo = Fileinfo(filepath)

        self.img_uri: str | None = None
        self.slide_num: int | None = None

        with h5py.File(filepath, "r") as f:
            self.attributes = dict(f.attrs)

        self.aux_1 = float(self.attributes.get("Aux1.Value","0"))*float(self.attributes.get("Aux1.ConversionFactor","0")) * (2 * float(self.attributes.get("Aux1.InvertSignalIn","0")) - 1)
        self.aux_1_unit = self.attributes.get("Aux1.Unit","")
        self.aux_1_label = self.attributes.get("Aux1.Label","")

        self.aux_2 = float(self.attributes.get("Aux2.Value","0"))*float(self.attributes.get("Aux2.ConversionFactor","0")) * (2 * float(self.attributes.get("Aux2.InvertSignalIn","0")) - 1)
        self.aux_2_unit = self.attributes.get("Aux2.Unit","")
        self.aux_2_label = self.attributes.get("Aux2.Label","")

        self.time_per_pixel = self.attributes.get("PI.ControlTimeStep","")
        self.time_per_pixel_unit = self.attributes.get("PI.ControlTimeStep.Unit","")

        super().__init__(filepath)

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
