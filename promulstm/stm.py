import numpy as np
import os
import io
import base64
import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar
import seaborn as sns

import config

plt.rcParams.update({"figure.max_open_warning": 0})


class StmImage:
    """
    Class for STM Images
    """

    def __init__(self, img_data, save_dir, save_name):
        self.img_data = img_data
        self.xsize, self.ysize = img_data.shape
        self.save_dir = save_dir
        self.save_name = save_name

    @property
    def shape(self):
        return self.img_data.shape

    def plot(self, save=config.save_stm_pngs, show=False):
        """
        Plots the image.
        """
        rocket = sns.color_palette("rocket", as_cmap=True)
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.imshow(
            self.img_data,
            cmap=rocket,
            vmin=None,
            vmax=None,
            origin="lower",
            extent=(0, self.xsize, 0, self.ysize),
        )
        # plt.colorbar()
        scalebar = ScaleBar(
            1,
            "nm",
            length_fraction=0.3,
            location="lower right",
            color="white",
            box_alpha=0,
        )
        ax.add_artist(scalebar)
        ax.tick_params(
            left=False,
            bottom=False,
            labelleft=False,
            labelbottom=False,
        )
        plt.tight_layout()

        png_bytes = io.BytesIO()
        extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
        plt.savefig(png_bytes, bbox_inches=extent)
        png_bytes.seek(0)
        png_data_uri = "data:image/png;base64, " + base64.b64encode(
            png_bytes.read()
        ).decode("ascii")

        if save is True:
            if not os.path.exists(self.save_dir):
                os.makedirs(self.save_dir)

            extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
            plt.savefig(
                os.path.join(self.save_dir, self.save_name + ".png"), bbox_inches=extent
            )

        if show is True:
            plt.show()

        return png_data_uri

    def fix_zero(self):
        """
        Subtracts the minimum value of the image array from the image array
        """
        self.img_data -= np.min(self.img_data)
        return self

    def corr_lines(self):
        """
        Subtracts a plane of the average of each scan line from the image array
        """
        mean = np.mean(self.img_data, axis=1)
        correction = np.broadcast_to(mean, self.img_data.shape).T
        self.img_data -= correction
        return self

    def corr_plane(self):
        """
        Subtracts a fitted background plane from the image array
        """
        x_shape, y_shape = self.img_data.shape
        x_coords = np.broadcast_to(np.arange(x_shape), self.img_data.shape)
        y_coords = np.repeat(np.arange(y_shape), y_shape).reshape(self.img_data.shape)

        coeff_matrix = np.column_stack(
            (np.ones(self.img_data.size), x_coords.flatten(), y_coords.flatten())
        )
        least_squares = np.linalg.lstsq(
            coeff_matrix, self.img_data.flatten(), rcond=-1
        )[0]

        correction = (
            least_squares[0] * np.ones(self.img_data.shape)
            + least_squares[1] * x_coords
            + least_squares[2] * y_coords
        )
        self.img_data -= correction
        return self
