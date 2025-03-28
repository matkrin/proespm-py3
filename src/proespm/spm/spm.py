import base64
import io
from typing import Any, Self, final

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib_scalebar.scalebar import ScaleBar  # pyright: ignore[reportMissingTypeStubs]
from numpy._typing import NDArray

plt.rcParams.update({"figure.max_open_warning": 0})


@final
class SpmImage:
    """Class for SPM image data

    Args:
        arr: Pixel data of the STM image
        xsize: Physical dimension of the STM image in x-direction

    """

    def __init__(self, arr: NDArray[np.floating[Any]], xsize: float) -> None:
        self.arr = arr
        self.yres, self.xres = arr.shape
        self.xsize = xsize
        self.data_uri = None

    @property
    def shape(self) -> tuple[int, int]:
        return self.arr.shape

    def plot(self, colormap: str, colorrange: tuple[float, float], show: bool = False) -> Self:
        """Plots the image in"""
        # rocket = sns.color_palette("rocket", as_cmap=True)
        # cmap = colormap
        # if colormap == "rocket":
        #     cmap = rocket
            
        vmin = np.percentile(self.arr, colorrange[0])
        vmax = np.percentile(self.arr, colorrange[1])
        fig, ax = plt.subplots(figsize=(5, 5))  # pyright: ignore[reportUnknownMemberType]
        _ = ax.imshow(  # pyright: ignore[reportUnknownMemberType]
            self.arr,
            cmap=colormap,
            vmin=vmin,
            vmax=vmax,
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
        _ = ax.add_artist(scalebar)
        ax.tick_params(  # pyright: ignore[reportUnknownMemberType]
            left=False,
            bottom=False,
            labelleft=False,
            labelbottom=False,
        )
        plt.tight_layout()

        png_bytes = io.BytesIO()
        extent = ax.get_window_extent().transformed(
            fig.dpi_scale_trans.inverted()
        )
        plt.savefig(png_bytes, bbox_inches=extent)  # pyright: ignore[reportUnknownMemberType]
        _ = png_bytes.seek(0)

        png_data_uri = "data:image/png;base64, " + base64.b64encode(
            png_bytes.read()
        ).decode("ascii")

        if show is True:
            plt.show()  # pyright: ignore[reportUnknownMemberType]

        self.data_uri = png_data_uri

        return self

    def fix_zero(self):
        """Subtract the minimum value of the image array from the image array"""
        self.arr -= np.min(self.arr)
        return self

    def corr_lines(self):
        """Subtract a plane of the average of each scan line from the image array"""
        mean: float = np.mean(self.arr, axis=1)
        correction = np.broadcast_to(
            mean, (self.arr.shape[1], self.arr.shape[0])
        ).T
        self.arr -= correction

        return self

    def corr_plane(self):
        """Subtract a fitted background plane from the image array"""
        y_shape, x_shape = self.arr.shape
        x_coords, y_coords = np.meshgrid(np.arange(x_shape), np.arange(y_shape))
        coeff_matrix = np.column_stack(
            (np.ones(self.arr.size), x_coords.ravel(), y_coords.ravel())
        )
        least_squares = np.linalg.lstsq(
            coeff_matrix, self.arr.ravel(), rcond=-1
        )[0]
        background: NDArray[np.floating[Any]] = (
            least_squares[0] * np.ones(self.arr.shape)
            + least_squares[1] * x_coords
            + least_squares[2] * y_coords
        )
        self.arr -= background

        return self
