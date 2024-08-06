import os
from datetime import datetime
from typing import Self

import mulfile
import numpy as np

from prosurf.fileinfo import Fileinfo
from prosurf.spm.spm import SpmImage


class StmMul:
    """Class for handling .mul files

    Args:
        filepath (str): Full path to the .mul file
    """

    def __init__(self, filepath: str) -> None:
        self.ident = "MUL"
        self.fileinfo = Fileinfo(filepath)
        self.slide_num: int | None = None

        self.m_id: str = self.fileinfo.filename
        self.datetime = datetime.fromtimestamp(os.path.getmtime(filepath))

        self.mulimages = mulfile.load(filepath)

        for mul_image in self.mulimages:  # type: ignore[reportUnknownMemeberType]
            mul_image.basename = self.fileinfo.basename
            mul_image.m_id = mul_image.img_id  # type: ignore[reportUnknownMemeberType]
            mul_image.img_data = SpmImage(
                np.flip(mul_image.img_data, axis=0),   # type: ignore[reportUnknownMemeberType]
                mul_image.xsize,  # type: ignore[reportUnknownMemeberType]
            )

    def process(self) -> Self:
        for mul_image in self.mulimages:  # type: ignore[reportUnknownMemeberType]
            mul_image.img_data.corr_plane().corr_lines().plot()  # type: ignore[reportUnknownMemeberType]

        return self
