import os
from datetime import datetime
from typing import Self

import mulfile
import numpy as np

from prosurf.fileinfo import Fileinfo
from prosurf.labjournal import Labjournal
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

        for mul_image in self.mulimages:  # pyright: ignore[reportUnknownVariableType]
            mul_image.basename = self.fileinfo.basename
            mul_image.fileinfo = self.fileinfo
            mul_image.m_id = mul_image.img_id  # pyright: ignore[reportUnknownMemberType]
            mul_image.img_data = SpmImage(
                np.flip(mul_image.img_data, axis=0),   # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
                mul_image.xsize,  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
            )
            mul_image.labjournal_data = None

    def process(self) -> Self:
        for mul_image in self.mulimages:  # pyright: ignore[reportUnknownVariableType]
            mul_image.img_data.corr_plane().corr_lines().plot()  # pyright: ignore[reportUnknownMemberType]

        return self

    def set_labjournal_data(self, labjournal: Labjournal) -> None:
        for mul_image in self.mulimages:   # pyright: ignore[reportUnknownVariableType]
            mul_image.labjournal_data = labjournal.extract_metadata_for_m_id(mul_image.m_id)   # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]




