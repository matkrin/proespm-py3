import os
import numpy as np
from typing import Optional

from sm4file import Sm4
from bokeh.embed import components

from proespm_py3.ec.ec import EcPlot
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

        for channel in self.sm4.topography_channels():
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

        e_cell_imgs = [ch for ch in self.sm4 if "VEC" in ch.label]
        u_tun_imgs = [ch for ch in self.sm4 if "Utun" in ch.label]

        if len(e_cell_imgs) != 0:
            e_cell_avg = np.average(e_cell_imgs[0].data, axis=0)
            u_tun_avg = np.average(u_tun_imgs[0].data, axis=0)
            x = np.arange(1, len(e_cell_avg) + 1)
            plot = EcPlot()
            plot.set_x_axis_label("Pixels average lines")
            plot.set_y_axis_label("U [V vs pt pseudo]")
            plot.plot_circle(x, e_cell_avg, legend_label="E_cell")
            plot.plot_circle(x, u_tun_avg, legend_label="U_tun")
            plot.fig.width = 500
            plot.fig.height = 500
            self.voltage_script, self.voltage_div = components(
                plot.fig, wrap_script=True
            )

        i_cell_imgs = [ch for ch in self.sm4 if "IEC" in ch.label]

        if len(i_cell_imgs) != 0:
            i_cell_avg = np.average(i_cell_imgs[0].data, axis=0)
            x = np.arange(1, len(i_cell_avg) + 1)
            plot = EcPlot()
            plot.set_x_axis_label("Pixels average lines")
            plot.set_y_axis_label("I [A]")
            plot.plot_circle(x, i_cell_avg)
            plot.show_legend(False)
            plot.fig.width = 500
            plot.fig.height = 500
            self.current_script, self.current_div = components(
                plot.fig, wrap_script=True
            )
