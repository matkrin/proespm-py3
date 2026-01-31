import base64
from datetime import datetime, timezone
from pathlib import Path
from typing import Self, final, override
import io

import h5py
from PIL import Image

from proespm.config import Config
from proespm.fileinfo import Fileinfo
from proespm.measurement import Measurement


@final
class ErrorTopography(Measurement):
    """Class for handling .h5 files of error topography (ET) measurements.

    Args:
        filepath (str): Full path to the .h5 file
    """

    op_mode = "ET"
    image_extensions = ("jpg", "jpeg")

    def __init__(self, filepath: str) -> None:
        self.fileinfo = Fileinfo(filepath)

        self.img_uri: str | None = None
        self.slide_num: int | None = None

        with h5py.File(filepath, "r") as f:
            self.attributes = dict(f.attrs)

        # TODO Maybe?
        self.time_per_pixel = self.attributes["PI.ControlTimeStep"]
        self.time_per_pixel_unit = self.attributes["PI.ControlTimeStep.Unit"]

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
        base_path = Path(self.fileinfo.filepath).with_suffix("")

        for ext in ErrorTopography.image_extensions:
            path = base_path.with_suffix(f".{ext}")
            if path.exists():
                image_path = path
                image_extension = ext
                break
        else:
            raise FileNotFoundError(
                f"No JPEG image found next to the .h5 file '{self.fileinfo.filepath}'"
            )

        with Image.open(image_path) as img:
            img = img.rotate(90, expand=True)
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG")
            encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
            self.img_uri = f"data:image/{image_extension};base64,{encoded}"

        return self

    @override
    def template_name(self) -> str:
        return "fastspm.j2"
