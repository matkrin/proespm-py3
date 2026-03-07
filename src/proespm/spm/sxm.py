from datetime import datetime
from typing import Self, final, override

import nanonispy as nap
import numpy as np
from dateutil import parser

from proespm.config import Config
from proespm.fileinfo import Fileinfo
from proespm.measurement import Measurement
from proespm.spm.spm import SpmImage


@final
class StmSxm(Measurement):
    """Class for handling Nanonis .sxm files

    Args:
        filepath (str): Full path to the .sxm file
    """

    def __init__(self, filepath: str) -> None:
        self.fileinfo = Fileinfo(filepath)
        self.slide_num: int | None = None

        self.sxm = nap.read.Scan(filepath)

        day, month, year = self.sxm.header["rec_date"].split(".")
        time = self.sxm.header["rec_time"]
        self._datetime = parser.parse(f"{year}-{month}-{day} {time}")

        self.current: float = (
            float(self.sxm.header["z-controller"]["Setpoint"][0].split()[0])
            * 1e9
        )  # in nA

        self.bias: float = self.sxm.header["bias"]

        self.xsize, self.ysize = self.sxm.header["scan_range"] * 1e9
        self.xoffset, self.yoffset = self.sxm.header["scan_offset"] * 1e9
        self.xres, self.yres = self.sxm.header["scan_pixels"]
        self.rotation = float(self.sxm.header["scan_angle"])
        self.line_time = self.sxm.header["scan_time"][0] * 1e3
        self.speed = self.line_time * self.yres / 1e3

        self.img_data_fw = SpmImage(
            np.flip(self.sxm.signals["Z"]["forward"], axis=0),
            self.xsize,
        )
        self.img_data_bw = SpmImage(
            np.flip(self.sxm.signals["Z"]["backward"], axis=(0, 1)),
            self.xsize,
        )

    @override
    def m_id(self) -> str:
        return self.fileinfo.filename

    @override
    def get_datetime(self) -> datetime:
        return self._datetime

    @override
    def process(self, config: Config) -> Self:
        _ = (
            self.img_data_fw.corr_plane()
            .corr_lines_median()
            .corr_plane()
            .corr_lines_median()
            .plot(config.colormap, config.colorrange)
        )
        _ = (
            self.img_data_bw.corr_plane()
            .corr_lines_median()
            .corr_plane()
            .corr_lines_median()
            .plot(config.colormap, config.colorrange)
        )
        return self

    @override
    def template_name(self) -> str:
        return "sxm.j2"
