import os
from datetime import datetime
from typing import Self

import mulfile
import numpy as np

from proespm.fileinfo import Fileinfo
from proespm.config import Config
from proespm.labjournal import Labjournal
from proespm.spm.spm import SpmImage


class StmMul:
    """Class for handling .mul files

    Args:
        filepath (str): Full path to the .mul file
    """

    ident = "MUL"

    def __init__(self, filepath: str) -> None:
        self.fileinfo = Fileinfo(filepath)
        self.slide_num: int | None = None

        self.m_id: str = self.fileinfo.filename
        self.sheet_id: str | None = None
        self.datetime = datetime.fromtimestamp(os.path.getmtime(filepath))

        self.mulimages = mulfile.load(filepath)

        for mul_image in self.mulimages:
            mul_image.basename = self.fileinfo.basename  # pyright: ignore[reportAttributeAccessIssue]
            mul_image.fileinfo = self.fileinfo  # pyright: ignore[reportAttributeAccessIssue]
            mul_image.m_id = mul_image.img_id  # pyright: ignore[reportAttributeAccessIssue]
            mul_image.img_data = SpmImage(  # pyright: ignore[reportAttributeAccessIssue]
                np.flip(mul_image.img_data, axis=0),
                mul_image.xsize,
            )
            mul_image.labjournal_data = None  # pyright: ignore[reportAttributeAccessIssue]

    def process(self, config: Config) -> Self:
        for mul_image in self.mulimages:
            mul_image.img_data.corr_plane().corr_lines().plot(
                config.colormap, config.colorrange
            )

        return self

    def set_labjournal_data(self, labjournal: Labjournal) -> None:
        for mul_image in self.mulimages:
            metadata = labjournal.extract_metadata_for_m_id(mul_image.m_id)  # pyright: ignore[reportAttributeAccessIssue]
            if metadata is not None:
                self.sheet_id, mul_image.labjournal_data = metadata
