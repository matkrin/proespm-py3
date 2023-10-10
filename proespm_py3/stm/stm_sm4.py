import os
import numpy as np
from typing import Optional

from sm4file import Sm4
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
        self.slide_num: Optional[int] = None

        self.m_id = self.filename
        self.png_save_dir = os.path.join(self.dirname, "sm4_png")

        self.sm4 = Sm4(filepath)

        for channel in self.sm4:
            if channel.scan_direction == "right":
                self.img_fw = channel
            elif channel.scan_direction == "left":
                self.img_bw = channel

        self.datetime = self.img_fw.datetime
        self.current = self.img_fw.current * 1e9  # in nA
        self.bias = self.img_fw.bias
        self.xoffset = self.img_fw.x_offset * 1e9  # in nm
        self.yoffset = self.img_fw.y_offset * 1e9  # in nm
        self.xres = self.img_fw.xres
        self.yres = self.img_fw.yres
        self.tilt = self.img_fw.angle  # in deg
        self.xsize = self.img_fw.xsize * 1e9  # in nm
        self.ysize = self.img_fw.ysize * 1e9  # in nm
        self.speed = self.img_fw.period * self.xres * self.yres
        self.line_time = self.img_fw.period * self.xres * 1e3  # in ms

        self.img_data_fw = StmImage(
            np.flip(self.img_fw.data * 1e9, axis=0), self.xsize
        )
        self.img_data_bw = StmImage(
            np.flip(self.img_bw.data * 1e9, axis=0), self.xsize
        )
