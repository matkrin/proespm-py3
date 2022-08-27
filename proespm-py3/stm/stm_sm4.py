import os
import numpy as np
import rhksm4
from dateutil import parser

from .stm import StmImage


class StmSm4:
    """Class for handling RHK SM4 files

    Args:
        filepath (str): Full path to the .sm4 files

    """

    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.basename = os.path.basename(self.filepath)
        self.dirname = os.path.dirname(self.filepath)
        self.filename, self.fileext = os.path.splitext(self.basename)

        self.m_id = self.filename
        self.png_save_dir = os.path.join(self.dirname, "sm4_png")

        self.sm4 = rhksm4.load(filepath)

        self.img_fw = self.sm4[8]
        self.img_bw = self.sm4[9]

        self.datetime = parser.parse(self.img_fw.attrs["RHK_DateTime"])

        self.current = self.img_fw.attrs["RHK_Current"]
        self.bias = self.img_fw.attrs["RHK_Bias"]

        self.xoffset = self.img_fw.attrs["RHK_Xoffset"] * 1e9  # in nm
        self.yoffset = self.img_fw.attrs["RHK_Yoffset"] * 1e9  # in nm

        self.xres = self.img_fw.attrs["RHK_Xsize"]
        self.yres = self.img_fw.attrs["RHK_Ysize"]
        self.tilt = self.img_fw.attrs["RHK_Angle"]  # in deg

        for param in self.img_fw.attrs["RHK_PRMdata"].split("\n"):
            if param.startswith("<1322>\tScan size"):
                self.xsize = (
                    float(param.split("::")[1].split()[0]) * 1e9
                )  # in nm
                self.ysize = self.xsize
            elif param.startswith("<1326>\tScan speed"):
                self.speed_mps = float(
                    param.split("::")[1].split()[0]
                )  # in m/s !!
            elif param.startswith("<1327>\tLine time"):
                self.line_time = (
                    float(param.split("::")[1].split()[0]) * 1e3
                )  # in ms

        self.speed = self.line_time * self.yres / 1e3  # in s

        self.img_data_fw = StmImage(
            np.flip(self.img_fw.data * 1e9), self.xsize
        )
        self.img_data_bw = StmImage(
            np.flip(self.img_bw.data * 1e9), self.xsize
        )
