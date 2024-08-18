from typing import Self
import numpy as np
from bokeh.embed import components
from numpy.typing import NDArray
from sm4file import Sm4

from prosurf.ec.ec import EcPlot
from prosurf.fileinfo import Fileinfo
from prosurf.labjournal import Labjournal
from prosurf.spm.spm import SpmImage


class StmSm4:
    """Class for handling RHK SM4 files

    Args:
        filepath (str): Full path to the .sm4 files
    """

    def __init__(self, filepath: str) -> None:
        self.ident = "SM4"
        self.fileinfo = Fileinfo(filepath)
        self.slide_num: int | None = None
        self.par5: str | None = None

        self.m_id = self.fileinfo.filename
        self.labjournal_data: dict[str, str] | None = None

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

        self.img_data_fw = SpmImage(self.img_fw.data * 1e9, self.xsize)
        self.img_data_bw = SpmImage(self.img_bw.data * 1e9, self.xsize)

        # Electrochemistry specific stuff (EC-STM)
        self.voltage_script = None
        self.voltage_div = None
        self.current_script = None
        self.current_div = None
        self.init_ec_data()

    def init_ec_data(self) -> None:
        e_cell_imgs = [
            ch for ch in self.sm4 if "VEC" in ch.label or "E_WE" in ch.label
        ]
        u_tun_imgs = [
            ch for ch in self.sm4 if "U_Tun" in ch.label or "Utun" in ch.label
        ]

        if len(e_cell_imgs) != 0:
            e_cell_avg: NDArray[np.float32] = np.average(
                e_cell_imgs[0].data, axis=0
            )
            u_tun_avg: NDArray[np.float32] = np.average(
                u_tun_imgs[0].data, axis=0
            )
            x = np.arange(1, len(e_cell_avg) + 1)

            plot = EcPlot()
            plot.set_x_axis_label("Pixels average lines")
            plot.set_y_axis_label("U [V vs pt pseudo]")
            plot.plot_scatter(x, e_cell_avg, legend_label="E_cell")
            plot.plot_scatter(x, u_tun_avg, legend_label="U_tun")
            plot.fig.width = 500
            plot.fig.height = 500
            self.voltage_script, self.voltage_div = components(
                plot.fig, wrap_script=True
            )

        i_cell_imgs = [
            ch for ch in self.sm4 if "I_WE" in ch.label or "IEC" in ch.label
        ]

        if len(i_cell_imgs) != 0:
            i_cell_avg: NDArray[np.float32] = np.average(
                i_cell_imgs[0].data, axis=1
            )
            if self.par5 is not None:
                i_cell_avg = i_cell_avg * float(self.par5)
            x = np.arange(1, len(i_cell_avg) + 1)
            plot = EcPlot()
            plot.set_x_axis_label("Pixels average lines")
            plot.set_y_axis_label("I [A]")
            plot.plot_scatter(x, i_cell_avg)
            plot.show_legend(False)
            plot.fig.width = 500
            plot.fig.height = 500
            self.current_script, self.current_div = components(
                plot.fig, wrap_script=True
            )

    def process(self) -> Self:
        _ = self.img_data_fw.corr_plane().corr_lines().plot()
        _ = self.img_data_bw.corr_plane().corr_lines().plot()
        return self

    def set_labjournal_data(self, labjournal: Labjournal) -> None:
        self.labjournal_data = labjournal.extract_metadata_for_m_id(self.m_id)
