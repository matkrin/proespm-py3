from datetime import datetime
import os
from typing import Self, final, override


from proespm.config import Config
from proespm.fastspm.fastspm import read_corresponding_image
from proespm.fileinfo import Fileinfo
from proespm.measurement import Measurement


@final
class ResonanceFrequency(Measurement):
    """Class for handling .h5 files of resonance frequency (RF) measurements.

    Args:
        filepath (str): Full path to the .h5 file
    """

    op_mode = "RF"

    def __init__(self, filepath: str) -> None:
        self.fileinfo = Fileinfo(filepath)

        self.img_uri = read_corresponding_image(
            self.fileinfo.filepath, rotate=True
        )
        self.slide_num: int | None = None

    @override
    def m_id(self) -> str:
        return self.fileinfo.filename

    @override
    def datetime(self) -> datetime:
        return datetime.fromtimestamp(os.path.getmtime(self.fileinfo.filepath))

    @override
    def process(self, config: Config) -> Self:
        return self

    @override
    def template_name(self) -> str:
        return "fastspm.j2"
