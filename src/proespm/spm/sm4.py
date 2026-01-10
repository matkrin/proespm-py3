from datetime import datetime
from typing import Self, final, override

import numpy as np
from bokeh.embed import components
from numpy.typing import NDArray
from sm4file import Sm4

from proespm.config import Config
from proespm.ec.ec import EcPlot
from proespm.fileinfo import Fileinfo
from proespm.measurement import Measurement
from proespm.spm.spm import SpmImage


@final
class StmSm4(Measurement):
    """Class for handling RHK SM4 files

    Args:
        filepath (str): Full path to the .sm4 files
    """

    def __init__(self, filepath: str) -> None:
        self.ident = "SM4"
        self.fileinfo = Fileinfo(filepath)
        self.slide_num: int | None = None
        self.par5: str | None = None

        self.sm4 = Sm4(filepath)

        for channel in self.sm4.topography_channels():
            if channel.scan_direction == "right":
                self.img_fw = channel
            elif channel.scan_direction == "left":
                self.img_bw = channel

        self._datetime = self.img_fw.datetime
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

        # If there is more than 2 current and 2 topography channels
        if len(self.sm4) > 4:
            self.init_ec_data()

    def init_ec_data(self) -> None:
        e_cell_imgs = [
            ch for ch in self.sm4 if "VEC" in ch.label or "E_WE" in ch.label
        ]
        u_tun_imgs = [
            ch for ch in self.sm4 if "U_Tun" in ch.label or "Utun" in ch.label
        ]

        if len(e_cell_imgs) != 0:
            e_cell_avg: NDArray[np.float32] = np.average(  # pyright: ignore[reportAny]
                e_cell_imgs[0].data, axis=0
            )
            x = np.arange(1, len(e_cell_avg) + 1)

            plot = EcPlot()
            plot.set_x_axis_label("y pixel")
            plot.set_y_axis_label("U line-averaged")
            plot.plot_scatter(x, e_cell_avg, legend_label="E_WE [V]")

            if len(u_tun_imgs) != 0:
                u_tun_avg: NDArray[np.float32] = np.average(  # pyright: ignore[reportAny]
                    u_tun_imgs[0].data, axis=0
                )
                plot.plot_scatter(x, u_tun_avg, legend_label="U_b [V]")

            plot.fig.width = 500
            plot.fig.height = 500
            self.voltage_script, self.voltage_div = components(
                plot.fig, wrap_script=True
            )

        i_cell_imgs = [
            ch for ch in self.sm4 if "I_WE" in ch.label or "IEC" in ch.label
        ]

        if len(i_cell_imgs) != 0:
            i_cell_avg: NDArray[np.float32] = np.average(  # pyright: ignore[reportAny]
                i_cell_imgs[0].data, axis=1
            )
            if self.par5 is not None:
                i_cell_avg = i_cell_avg * float(self.par5)
            x = np.arange(1, len(i_cell_avg) + 1)
            plot = EcPlot()
            plot.set_x_axis_label("y pixel")
            plot.set_y_axis_label("I_WE line-averaged[V]")
            plot.plot_scatter(x, i_cell_avg)
            plot.show_legend(False)
            plot.fig.width = 500
            plot.fig.height = 500
            self.current_script, self.current_div = components(
                plot.fig, wrap_script=True
            )

    @override
    def m_id(self) -> str:
        return self.fileinfo.filename

    @override
    def datetime(self) -> datetime:
        return self._datetime

    @override
    def process(self, config: Config) -> Self:
        _ = (
            self.img_data_fw.corr_plane()
            .corr_lines_median()
            .corr_plane()
            .corr_lines_median()
            .plot(config.colormap, config.colorrange)
        )
        _ = (
            self.img_data_bw.corr_plane()
            .corr_lines_median()
            .corr_plane()
            .corr_lines_median()
            .plot(config.colormap, config.colorrange)
        )

        return self

    @override
    def template_name(self) -> str:
        return "sm4.j2"
