import numpy as np
import os
import io
import base64
import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar
import seaborn as sns


plt.rcParams.update({"figure.max_open_warning": 0})


class StmImage:
    """Class for STM Image Arrays

    Args:
        arr (numpy.ndarray): Pixel data of the STM image
        xsize (float | int): Physical dimension of the STM image in x-direction

    """

    def __init__(self, arr, xsize):
        self.arr = arr
        self.yres, self.xres = arr.shape
        self.xsize = xsize

    @property
    def shape(self):
        return self.arr.shape

    def plot(self, show=False, save=False, save_dir="", save_name=""):
        """
        Plots the image.
        """
        rocket = sns.color_palette("rocket", as_cmap=True)
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.imshow(  # type: ignore
            self.arr,
            cmap=rocket,
            vmin=None,
            vmax=None,
            origin="lower",
            extent=(0, self.xres, 0, self.yres),
        )
        # plt.colorbar()
        scalebar = ScaleBar(
            self.xsize / self.xres,
            "nm",
            length_fraction=0.25,
            location="lower right",
            color="white",
            box_alpha=0,
        )
        ax.add_artist(scalebar)  # type: ignore
        ax.tick_params(  # type: ignore
            left=False,
            bottom=False,
            labelleft=False,
            labelbottom=False,
        )
        plt.tight_layout()

        png_bytes = io.BytesIO()
        extent = ax.get_window_extent().transformed(  # type: ignore
            fig.dpi_scale_trans.inverted()  # type: ignore
        )
        plt.savefig(png_bytes, bbox_inches=extent)
        png_bytes.seek(0)
        png_data_uri = "data:image/png;base64, " + base64.b64encode(
            png_bytes.read()
        ).decode("ascii")

        if save is True:
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            extent = ax.get_window_extent().transformed(  # type: ignore
                fig.dpi_scale_trans.inverted()  # type: ignore
            )
            plt.savefig(
                os.path.join(save_dir, save_name + ".png"), bbox_inches=extent
            )

        if show is True:
            plt.show()

        self.data_uri = png_data_uri
        return self

    def fix_zero(self):
        """
        Subtract the minimum value of the image array from the image array
        """
        self.arr -= np.min(self.arr)
        return self

    def corr_lines(self):
        """
        Subtract a plane of the average of each scan line from the image array
        """
        mean = np.mean(self.arr, axis=1)
        correction = np.broadcast_to(
            mean, (self.arr.shape[1], self.arr.shape[0])
        ).T
        self.arr -= correction
        return self

    def corr_plane(self):
        """
        Subtract a fitted background plane from the image array
        """
        y_shape, x_shape = self.arr.shape
        x_coords, y_coords = np.meshgrid(
            np.arange(x_shape), np.arange(y_shape)
        )
        coeff_matrix = np.column_stack(
            (np.ones(self.arr.size), x_coords.ravel(), y_coords.ravel())
        )
        least_squares = np.linalg.lstsq(
            coeff_matrix, self.arr.ravel(), rcond=-1
        )[0]
        background = (
            least_squares[0] * np.ones(self.arr.shape)
            + least_squares[1] * x_coords
            + least_squares[2] * y_coords
        )
        self.arr -= background
        return self
