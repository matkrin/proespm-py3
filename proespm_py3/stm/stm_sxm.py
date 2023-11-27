import os
from typing import Optional
import numpy as np
from dateutil import parser
import nanonispy as nap
from .stm import StmImage


class StmSxm:
    """Class for handling Nanonis .sxm files

    Args:
        filepath (str): Full path to the .sxm file

    """

    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.basename = os.path.basename(self.filepath)
        self.dirname = os.path.dirname(self.filepath)
        self.filename, self.fileext = os.path.splitext(self.basename)
        self.slide_num: Optional[int] = None

        self.m_id = self.filename
        self.sheet_id: str | None = None
        self.png_save_dir = os.path.join(self.dirname, "sxm_png")

        self.sxm = nap.read.Scan(filepath)

        day, month, year = self.sxm.header["rec_date"].split(".")
        time = self.sxm.header["rec_time"]
        self.datetime = parser.parse(f"{year}-{month}-{day} {time}")

        self.current = (
            float(self.sxm.header["z-controller"]["Setpoint"][0].split()[0])
            * 1e9
        )  # in nA

        self.bias = self.sxm.header["bias"]  # in V

        self.xsize, self.ysize = self.sxm.header["scan_range"] * 1e9  # in nm
        self.xoffset, self.yoffset = self.sxm.header["scan_offset"] * 1e9
        self.xres, self.yres = self.sxm.header["scan_pixels"]
        self.tilt = float(self.sxm.header["scan_angle"])  # in deg?
        self.line_time = self.sxm.header["scan_time"][0] * 1e3  # in s?
        self.speed = self.line_time * self.yres / 1e3  # in s?

        self.img_data_fw = StmImage(
            self.sxm.signals["Z"]["forward"], self.xsize
        )
        self.img_data_bw = StmImage(
            np.flip(self.sxm.signals["Z"]["backward"], axis=1), self.xsize
        )
