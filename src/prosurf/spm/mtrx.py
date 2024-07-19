import os
from datetime import datetime
import numpy as np
import access2thematrix  # type: ignore[reportMissingTypeStubs]

from prosurf.spm.spm import SpmImage


class NoTracesError(Exception):
    def __init__(self, filename: str) -> None:
        message = f"{filename} contains no traces"
        super().__init__(message)


class Fileinfo:
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.basename = os.path.basename(self.filepath)
        self.dirname = os.path.dirname(self.filepath)
        self.filename, self.fileext = os.path.splitext(self.basename)


class StmMatrix:
    """Class for handling Omicron .Z_mtrx files

    Args:
        filepath (str): Full path to the .Z_mtrx file

    """

    def __init__(self, filepath: str) -> None:
        self.ident = "MTRX"
        self.fileinfo = Fileinfo(filepath)
        self.slide_num: int | None = None

        self.m_id: str = self.fileinfo.filename
        self.sheet_id: str | None = None

        self.datetime = datetime.fromtimestamp(os.path.getmtime(filepath))

        mtrx_data = access2thematrix.MtrxData()

        self.traces, _ = mtrx_data.open(filepath)  # type: ignore[unknownMemberType]
        if self.traces == {}:  # type: ignore[unknownMemberType]
            raise NoTracesError(self.fileinfo.filename)

        img_fw = mtrx_data.select_image(self.traces[0])[0]  # type: ignore[unknownMemberType]
        img_bw = mtrx_data.select_image(self.traces[1])[0]  # type: ignore[unknownMemberType]

        self.creation_comment = mtrx_data.creation_comment
        self.data_set_name = mtrx_data.data_set_name
        self.sample_name = mtrx_data.sample_name

        self.yres, self.xres = img_fw.data.shape  # type: ignore[unknownMemberType]
        self.xsize = img_fw.width * 1e9  # in nm
        self.ysize = img_fw.height * 1e9  # in nm
        self.xoffset = img_fw.x_offset  # in nm
        self.yoffset = img_fw.y_offset  # in nm
        self.rotation = img_fw.angle  # in deg

        meta = mtrx_data.get_experiment_element_parameters()[1]
        for param in meta.split("\n"):
            # print(f"{param=}")
            if param.startswith("Regulator.Setpoint_1"):
                self.current = float(param.split()[1]) * 1e9  # in nA
            elif param.startswith("GapVoltageControl.Voltage "):
                self.bias = float(param.split()[1]) * 1e3  # in mV
            elif param.startswith("XYScanner.Raster_Time "):
                # in seconds, per pixel?
                self.raster_time = float(param.split()[1])

        self.line_time = self.raster_time * self.xres * 1e3  # in ms
        self.scan_duration = self.line_time * self.yres / 1e3  # in s

        row_fw = np.flip(img_fw.data, axis=0) * 1e9  # type: ignore[reportUnknownMember] # in nm
        row_bw = np.flip(img_bw.data, axis=0) * 1e9  # type: ignore[reportUnknownMember] # in nm
        self.img_data_fw = SpmImage(row_fw, self.xsize)
        self.img_data_bw = SpmImage(row_bw, self.xsize)

    def process(self):
        _ = self.img_data_fw.corr_plane().corr_lines().plot()
        _ = self.img_data_bw.corr_plane().corr_lines().plot()
