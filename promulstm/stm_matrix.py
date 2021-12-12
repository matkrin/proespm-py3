import os
import datetime
import access2thematrix
from rich import print
from stm import Stm

class StmMatrix(Stm):

    def __init__(self, filepath):
        self.filepath = filepath
        self.basename = os.path.basename(self.filepath)
        self.dirname = os.path.dirname(self.filepath)
        self.filename, self.fileext = os.path.splitext(self.basename)
        self.m_id = self.filename
        self.png_save_dir = os.path.join(self.dirname, 'matrix_png')

        self.datetime = datetime.datetime.utcfromtimestamp(
            os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M:%S')

        self.mtrx_data = access2thematrix.MtrxData()
        self.traces = self.mtrx_data.open(filepath)[0]
        self.meta = self.mtrx_data.get_experiment_element_parameters()[1]

        self.img_fw = self.mtrx_data.select_image(self.traces[0])[0]
        self.img_bw = self.mtrx_data.select_image(self.traces[1])[0]

        self.img_data_fw = self.img_fw.data * 1e9       # in nm
        self.img_data_bw = self.img_bw.data * 1e9       # in nm
        self.xsize = self.img_fw.width * 1e9            # in nm
        self.ysize = self.img_fw.height * 1e9           # in nm
        self.xoffset = self.img_fw.x_offset             # in nm
        self.yoffset = self.img_fw.y_offset             # in nm
        self.yres, self.xres = self.img_data_fw.shape
        self.tilt = self.img_fw.angle                   # in deg

        for param in self.meta.split('\n'):
            if param.startswith('Regulator.Setpoint_1'):
                self.current = float(param.split()[1]) * 1e9        # in nA
            elif param.startswith('GapVoltageControl.Voltage '):
                self.bias = float(param.split()[1]) * 1e3           # in mV
            elif param.startswith('XYScanner.Raster_Time '):
                self.raster_time = float(param.split()[1])          # in seconds! per pixel?

        self.line_time = self.raster_time * self.xres * 1e3         # in ms
        self.speed = self.line_time * self.yres / 1e3               # in s


    def plot_fw(self, save=False, show=False):
        """
        returns method from Stm with parameters to plot the forward image of a
        matrix-file
        """
        self.png_str_fw = super().plot(
            img_array = self.img_data_fw,
            xsize = self.xsize,
            ysize = self.ysize,
            save_dir = self.png_save_dir,
            save_name = self.m_id + '_fw',
            save=save,
            show=show
            )


    def plot_bw(self, save=False, show=False):
        """
        method from Stm with parameters to plot the backward image of a
        matrix-file
        """
        self.png_str_bw =  super().plot(
            img_array = self.img_data_bw,
            xsize = self.xsize,
            ysize = self.ysize,
            save_dir = self.png_save_dir,
            save_name = self.m_id + '_bw',
            save=save,
            show=show
        )
