import os
import datetime
import access2thematrix
from .stm import StmImage


class NoTracesError(Exception):
    def __init__(self, filename) -> None:
        message = f"{filename} contains no traces"
        super().__init__(message)


class StmMatrix:
    """Class for handling Omicron .Z_mtrx files

    Args:
        filepath (str): Full path to the .Z_mtrx file

    """

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.basename = os.path.basename(self.filepath)
        self.dirname = os.path.dirname(self.filepath)
        self.filename, self.fileext = os.path.splitext(self.basename)

        self.m_id = self.filename
        self.png_save_dir = os.path.join(self.dirname, "matrix_png")

        self.datetime = datetime.datetime.utcfromtimestamp(
            os.path.getmtime(filepath)
        )

        self.mtrx_data = access2thematrix.MtrxData()
        self.traces = self.mtrx_data.open(filepath)[0]
        if self.traces == {}:
            raise NoTracesError(self.filename)

        self.meta = self.mtrx_data.get_experiment_element_parameters()[1]

        print(self.basename)
        print(self.traces)
        self.img_fw = self.mtrx_data.select_image(self.traces[0])[0]
        self.img_bw = self.mtrx_data.select_image(self.traces[1])[0]

        self.yres, self.xres = self.img_fw.data.shape
        self.xsize = self.img_fw.width * 1e9  # in nm
        self.ysize = self.img_fw.height * 1e9  # in nm
        self.xoffset = self.img_fw.x_offset  # in nm
        self.yoffset = self.img_fw.y_offset  # in nm
        self.tilt = self.img_fw.angle  # in deg

        for param in self.meta.split("\n"):
            if param.startswith("Regulator.Setpoint_1"):
                self.current = float(param.split()[1]) * 1e9  # in nA
            elif param.startswith("GapVoltageControl.Voltage "):
                self.bias = float(param.split()[1]) * 1e3  # in mV
            elif param.startswith("XYScanner.Raster_Time "):
                self.raster_time = float(
                    param.split()[1]
                )  # in seconds! per pixel?

        self.line_time = self.raster_time * self.xres * 1e3  # in ms
        self.speed = self.line_time * self.yres / 1e3  # in s

        self.img_data_fw = StmImage(
            self.img_fw.data * 1e9, self.xsize
        )  # in nm
        self.img_data_bw = StmImage(
            self.img_bw.data * 1e9, self.xsize
        )  # in nm
