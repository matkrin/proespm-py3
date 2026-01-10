import os
from datetime import datetime
from typing import Self

import mulfile
from mulfile.mul import Mul
import numpy as np

from proespm.fileinfo import Fileinfo
from proespm.config import Config
from proespm.spm.spm import SpmImage


class StmMul:
    """Class for handling .mul files

    Args:
        filepath (str): Full path to the .mul file
    """

    ident: str = "MUL"

    def __init__(self, filepath: str) -> None:
        self.fileinfo: Fileinfo = Fileinfo(filepath)
        self.slide_num: int | None = None

        self.m_id: str = self.fileinfo.filename
        self.datetime: datetime = datetime.fromtimestamp(
            os.path.getmtime(filepath)
        )

        self.mulimages: Mul = mulfile.load(filepath)

        for mul_image in self.mulimages:
            mul_image.basename = self.fileinfo.basename  # pyright: ignore[reportAttributeAccessIssue]
            mul_image.fileinfo = self.fileinfo  # pyright: ignore[reportAttributeAccessIssue]
            mul_image.m_id = mul_image.img_id  # pyright: ignore[reportAttributeAccessIssue]
            mul_image.img_data = SpmImage(  # pyright: ignore[reportAttributeAccessIssue]
                np.flip(mul_image.img_data, axis=0),
                mul_image.xsize,
            )

    def process(self, config: Config) -> Self:
        for mul_image in self.mulimages:
            (
                mul_image.img_data.corr_plane()
                .corr_lines_median()
                .corr_plane()
                .corr_lines_median()
                .plot(config.colormap, config.colorrange)
            )

        return self

    def template_name(self) -> str:
        return "mul.j2"
