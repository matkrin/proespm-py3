import os
import datetime
import numpy as np
import nanonispy as nap
from stm import Stm


class StmSxm(Stm):

    def __init__(self, filepath):
        self.filepath = filepath
        self.basename = os.path.basename(self.filepath)
        self.dirname = os.path.dirname(self.filepath)
        self.filename, self.fileext = os.path.splitext(self.basename)
        self.m_id = self.filename
        self.png_save_dir = os.path.join(self.dirname, 'sxm_png')

        self.sxm = nap.read.Scan(filepath)

        day, month, year = self.sxm.header['rec_date'].split('.')
        time = self.sxm.header['rec_time']
        self.datetime = f'{year}-{month}-{day} {time}'

        self.img_data_fw = self.sxm.signals['Z']['forward']
        self.img_data_bw = self.sxm.signals['Z']['backward']

        self.current = float(
            self.sxm.header['z-controller']['Setpoint'][0].split()[0]
        ) * 1e9  # in nA 

        self.bias = self.sxm.header['bias']  # in V

        self.xsize, self.ysize = self.sxm.header['scan_range'] * 1e9  # in nm
        self.xoffset, self.yoffset = self.sxm.header['scan_offset'] * 1e9
        self.xres, self.yres = self.sxm.header['scan_pixels']
        self.tilt = float(self.sxm.header['scan_angle'])  # in deg?
        self.line_time = self.sxm.header['scan_time'][0] * 1e3  # in s?
        self.speed = self.line_time * self.yres / 1e3 # in s?

    def plot_fw(self, save=True, show=False):
        return super().plot(
            img_array = self.img_data_fw,
            xsize = self.xsize,
            ysize = self.ysize,
            save_dir = self.png_save_dir,
            save_name = self.m_id + '_fw',
            save = save,
            show = show
        )

    def plot_bw(self, save=True, show=False):
        return super().plot(
            img_array = np.flip(self.img_data_bw, axis=1),
            xsize = self.xsize,
            ysize = self.ysize,
            save_dir = self.png_save_dir,
            save_name = self.m_id + '_bw',
            save = save,
            show = show
        )

    def add_png(self):
        self.png_str_fw = super().add_png(save_dir=self.png_save_dir,
                                           png_name=self.m_id + '_fw')

        self.png_str_bw = super().add_png(save_dir=self.png_save_dir,
                                           png_name=self.m_id + '_bw')
