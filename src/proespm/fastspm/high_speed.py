from datetime import datetime, timezone
from typing import Self, final, override

import h5py

from proespm.config import Config
from proespm.fastspm.fastspm import read_corresponding_image, read_corresponding_par_file
from proespm.fileinfo import Fileinfo
from proespm.measurement import Measurement


@final
class HighSpeed(Measurement):
    """Class for handling .h5 files of high speed (HS) measurements.

    Args:
        filepath (str): Full path to the .h5 file
    """

    op_mode = "HS"

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

        self.sig_in_convfact = float(self.attributes.get("Signal_In.ConversionFactor","nan"))
        self.sig_in_logamp = self.attributes.get("Signal_In.LogAmp","")
        self.sig_in_offset = float(self.attributes.get("Signal_In.Offset","nan"))
        self._sig_in_offset_unit = self.attributes.get("Signal_In.Offset.Unit","")
        self.sig_in_unit = self.attributes.get("Signal_In.Unit","")

        self.z_in_convfact = self.attributes.get("Z_In.ConversionFactor","")
        self.z_in_offset = self.attributes.get("Z_In.Offset","")
        self.z_in_offset_unit = self.attributes.get("Z_In.Offset.Unit","")
        self.z_in_unit = self.attributes.get("Z_In.Unit","")

        self.temp_start = self.attributes.get("ExperimentInfo.TemperatureStart","nan")
        self.temp_end = self.attributes.get("ExperimentInfo.TemperatureEnd","nan")
        self.temp_unit = self.attributes.get("ExperimentInfo.Temperature.Unit","nan")

        self.timestep = self.attributes.get("PI.ControlTimeStep","")
        self.timestep_unit = self.attributes.get("PI.ControlTimeStep.Unit","")

        self.par = read_corresponding_par_file(filepath)

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
