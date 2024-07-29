import numpy as np
from dateutil import parser
import nanonispy as nap  # type: ignore[reportMissingStubs]

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

        day, month, year = self.sxm.header["rec_date"].split(".")  # type: ignore[reportUnknownMemberType]
        time = self.sxm.header["rec_time"]  # type: ignore[reportUnknownMemberType]
        self.datetime = parser.parse(f"{year}-{month}-{day} {time}")

        self.current: float = (
            float(self.sxm.header["z-controller"]["Setpoint"][0].split()[0])  # type: ignore[reportUnknownMemberType]
            * 1e9
        )  # in nA

        self.bias: float = self.sxm.header["bias"]  # type:ignore[reportUnknownMemberType] in V

        self.xsize, self.ysize = self.sxm.header["scan_range"] * 1e9  # type:ignore[reportUnknownMemberType] in nm
        self.xoffset, self.yoffset = self.sxm.header["scan_offset"] * 1e9  # type:ignore[reportUnknownMemberType]
        self.xres, self.yres = self.sxm.header["scan_pixels"]  # type:ignore[reportUnknownMemberType]
        self.rotation = float(self.sxm.header["scan_angle"])  # type:ignore[reportUnknownMemberType] in deg?
        self.line_time = self.sxm.header["scan_time"][0] * 1e3  # type:ignore[reportUnknownMemberType]  in s?
        self.speed = self.line_time * self.yres / 1e3  # type:ignore[reportUnknownMemberType] in s?

        self.img_data_fw = SpmImage(
            np.flip(self.sxm.signals["Z"]["forward"], axis=0), self.xsize,  # type:ignore[reportUnknownArgumentType]
        )
        self.img_data_bw = SpmImage(
            np.flip(self.sxm.signals["Z"]["backward"], axis=(0, 1)), self.xsize,  # type:ignore[reportUnknownArgumentType]
        )

    def process(self):
        _ = self.img_data_fw.corr_plane().corr_lines().plot()
        _ = self.img_data_bw.corr_plane().corr_lines().plot()
