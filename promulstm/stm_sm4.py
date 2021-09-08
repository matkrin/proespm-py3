import os
import datetime
import numpy as np
import rhksm4
from stm import Stm


class StmSm4(Stm):

    def __init__(self, filepath):
        self.filepath = filepath
        self.basename = os.path.basename(self.filepath)
        self.dirname = os.path.dirname(self.filepath)
        self.filename, self.fileext = os.path.splitext(self.basename)
        self.m_id = self.filename
        self.png_save_dir = os.path.join(self.dirname, 'sm4_png')

        self.sm4 = rhksm4.load(filepath)

        self.img_fw = self.sm4[8]
        self.img_bw = self.sm4[9]

        self.datetime = self.img_fw.attrs['RHK_DateTime']

        self.img_data_fw = self.img_fw.data * 1e9       # in nm
        self.img_data_bw = self.img_bw.data * 1e9       # in nm
        
        self.current = self.img_fw.attrs['RHK_Current']
        self.bias = self.img_fw.attrs['RHK_Bias']

        #self.xsize = self.img_fw[''] * 1e9            # in nm
        #self.ysize = self.img_fw.height * 1e9           # in nm

        self.xoffset = self.img_fw.attrs['RHK_Xoffset'] * 1e9        # in nm
        self.yoffset = self.img_fw.attrs['RHK_Yoffset'] * 1e9        # in nm

        self.xres = self.img_fw.attrs['RHK_Xsize']
        self.yres = self.img_fw.attrs['RHK_Ysize']
        self.tilt = self.img_fw.attrs['RHK_Angle']                   # in deg

        for param in self.img_fw.attrs['RHK_PRMdata'].split('\n'):
            if param.startswith('<1322>\tScan size'):
                self.xsize = float(param.split('::')[1].split()[0]) * 1e9   # in nm
                self.ysize = self.xsize
            elif param.startswith('<1326>\tScan speed'):
                self.speed_mps = float(param.split('::')[1].split()[0]) # in m/s !!
            elif param.startswith('<1327>\tLine time'):
                self.line_time = float(param.split('::')[1].split()[0]) *1e3 # in ms

        self.speed = self.line_time * self.yres / 1e3   # in s


    def plot_fw(self, save=True, show=False):
        return super().plot(
            img_array = np.flip(self.img_data_fw),
            xsize = self.xsize,
            ysize = self.ysize,
            save_dir = self.png_save_dir,
            save_name = self.m_id + '_fw',
            save = save,
            show = show
        )

    def plot_bw(self, save=True, show=False):
        return super().plot(
            img_array = np.flip(self.img_data_bw),
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

