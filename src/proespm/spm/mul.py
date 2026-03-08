from pathlib import Path
from datetime import datetime
from typing import Self, override

import mulfile
from mulfile.mul import Mul
import numpy as np

from proespm.fileinfo import Fileinfo
from proespm.config import Config
from proespm.measurement import Measurement
from proespm.spm.spm import SpmImage


class StmMul(Measurement):
    """Class for handling .mul files

    Args:
        filepath (str): Full path to the .mul file
    """

    def __init__(self, filepath: Path) -> None:
        self.fileinfo: Fileinfo = Fileinfo(filepath)
        self.slide_num: int | None = None

        self.mulimages: Mul = mulfile.load(filepath)

        for mul_image in self.mulimages:
            mul_image.basename = self.fileinfo.basename  # ty:ignore[unresolved-attribute]
            mul_image.fileinfo = self.fileinfo  # ty:ignore[unresolved-attribute]
            mul_image.m_id = mul_image.img_id  # ty:ignore[unresolved-attribute]
            mul_image.img_data = SpmImage(  # ty:ignore[invalid-assignment]
                np.flip(mul_image.img_data, axis=0),
                mul_image.xsize,
            )

    @override
    def m_id(self) -> str:
        return self.fileinfo.filename

    @override
    def get_datetime(self) -> datetime:
        return self.mulimages[0].datetime

    @override
    def process(self, config: Config) -> Self:
        for mul_image in self.mulimages:
            (
                mul_image.img_data.corr_plane()  # ty:ignore[unresolved-attribute]
                .corr_lines_median()
                .corr_plane()
                .corr_lines_median()
                .plot(config.colormap, config.colorrange)
            )

        return self

    @override
    def template_name(self) -> str | None:
        return "mul.j2"
