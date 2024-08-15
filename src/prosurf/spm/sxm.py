from typing import Self
import numpy as np
from dateutil import parser
import nanonispy as nap  # pyright: ignore[reportMissingTypeStubs]

from prosurf.fileinfo import Fileinfo
from prosurf.spm.spm import SpmImage


class StmSxm:
    """Class for handling Nanonis .sxm files

    Args:
        filepath (str): Full path to the .sxm file
    """

    def __init__(self, filepath: str) -> None:
        self.ident = "SXM"
        self.fileinfo = Fileinfo(filepath)
        self.m_id = self.fileinfo.filename
        self.slide_num: int | None = None

        self.sxm = nap.read.Scan(filepath)

        day, month, year = self.sxm.header["rec_date"].split(".")  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
        time = self.sxm.header["rec_time"]  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
        self.datetime = parser.parse(f"{year}-{month}-{day} {time}")

        self.current: float = (
            float(self.sxm.header["z-controller"]["Setpoint"][0].split()[0])  # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType]
            * 1e9
        )  # in nA

        self.bias: float = self.sxm.header["bias"]  # pyright: ignore[reportUnknownMemberType] in V

        self.xsize, self.ysize = self.sxm.header["scan_range"] * 1e9  # pyright: ignore[reportUnknownMemberType] in nm
        self.xoffset, self.yoffset = self.sxm.header["scan_offset"] * 1e9  # pyright: ignore[reportUnknownMemberType]
        self.xres, self.yres = self.sxm.header["scan_pixels"]  # pyright: ignore[reportUnknownMemberType]
        self.rotation = float(self.sxm.header["scan_angle"])  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType] in deg?
        self.line_time = self.sxm.header["scan_time"][0] * 1e3  # pyright: ignore[reportUnknownMemberType]  in s?
        self.speed = self.line_time * self.yres / 1e3  # pyright: ignore[reportUnknownMemberType] in s?

        self.img_data_fw = SpmImage(
            np.flip(self.sxm.signals["Z"]["forward"], axis=0), self.xsize,  # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType]
        )
        self.img_data_bw = SpmImage(
            np.flip(self.sxm.signals["Z"]["backward"], axis=(0, 1)), self.xsize,  # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType]
        )

    def process(self) -> Self:
        _ = self.img_data_fw.corr_plane().corr_lines().plot()
        _ = self.img_data_bw.corr_plane().corr_lines().plot()
        return self
