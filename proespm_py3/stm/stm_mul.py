import os

import mulfile
from mulfile.mul import Mul
from .stm import StmImage


class StmMul(Mul):
    """Class for handling .mul files

    Args:
        filepath (str): Full path to the .mul file

    """

    def __init__(self, filepath: str) -> None:
        super().__init__(mulfile.load(filepath))

        self.filepath = filepath
        self.basename = os.path.basename(self.filepath)
        self.dirname = os.path.dirname(self.filepath)
        self.filename, self.fileext = os.path.splitext(self.basename)

        self.png_save_dir = os.path.join(self.dirname, self.filename + "_png")

        for mul_image in self.data:
            mul_image.basename = self.basename
            mul_image.png_save_dir = self.png_save_dir
            mul_image.m_id = mul_image.img_id
            mul_image.img_data = StmImage(mul_image.img_data, mul_image.xsize)
