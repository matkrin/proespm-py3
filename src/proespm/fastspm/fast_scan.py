import base64
from datetime import datetime, timezone
from pathlib import Path
from typing import Self, final, override

import h5py

from proespm.config import Config
from proespm.fileinfo import Fileinfo
from proespm.measurement import Measurement


IMAGE_EXTENSION = "jpg"


@final
class FastScan(Measurement):
    """Class for handling .h5 files of fast scans (FS)

    Args:
        filepath (str): Full path to the .h5 file
    """

    op_mode = "FS"

    def __init__(self, filepath: str) -> None:
        self.fileinfo = Fileinfo(filepath)
        print(self.fileinfo)

        self.img_uri: str | None = None
        self.slide_num: int | None = None

        with h5py.File(filepath, mode="r") as f:
            self.attributes = dict(f["data"].attrs)

        self.x_phase = self.attributes["Acquisition.X_Phase"]
        self.x_phase_unit = self.attributes["Acquisition.X_Phase.Unit"]

        self.y_phase = self.attributes["Acquisition.Y_Phase"]
        self.y_phase_unit = self.attributes["Acquisition.Y_Phase.Unit"]

        self.angle = self.attributes["Scanner.Angle"]
        self.angle_unit = self.attributes["Scanner.Angle.Unit"]

        self.x_frequency = self.attributes["Scanner.X_Frequency"]
        self.x_frequency_unit = self.attributes["Scanner.X_Frequency.Unit"]

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
        with (
            Path(self.fileinfo.filepath)
            .with_suffix(f".{IMAGE_EXTENSION}")
            .open("rb") as image_file
        ):
            self.img_uri = (
                f"data:image/{IMAGE_EXTENSION};base64, "
                + base64.b64encode(image_file.read()).decode("ascii")
            )

        return self

    @override
    def template_name(self) -> str:
        return "fastspm.j2"
