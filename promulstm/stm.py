import numpy as np
import os
import base64
import datetime
import matplotlib.pyplot as plt
plt.rcParams.update({'figure.max_open_warning': 0})
from matplotlib import transforms
from matplotlib_scalebar.scalebar import ScaleBar
import seaborn as sns
from pySPM import SPM


class Stm:

    def stm_plot(self, img_array, xsize, ysize, save_dir, save_name, save=False, show=False):
        """
        Plot the image.
        """
        rocket = sns.color_palette("rocket", as_cmap=True)
        fig, ax = plt.subplots(figsize=(5,5))
        ax.imshow(
            img_array,
            cmap=rocket,
            vmin=None,
            vmax=None,
            origin='lower',
            extent=(0, xsize, 0, ysize),
        )
        #plt.colorbar()
        scalebar = ScaleBar(
            1,
            "nm",
            length_fraction=0.3,
            location='lower right',
            color='white',
            box_alpha=0
        )
        ax.add_artist(scalebar)
        ax.tick_params(
            left=False,
            bottom=False,
            labelleft=False,
            labelbottom=False
        )
        plt.tight_layout()

        if save is True:
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
            plt.savefig(os.path.join(save_dir, save_name + '.png'), bbox_inches=extent)

        if show is True:
            plt.show()
        return fig


    def stm_add_png(self, save_dir, png_name):
        """
        adds the png encoded string to the image dictionary when save=True
        for plot
        base64 encode: encodes png to bytes type
        decode: makes a string out of byte type
        """
        png_dir = save_dir
        with open(os.path.join(png_dir, png_name + ".png"), 'rb') as f:
            png_str = 'data:image/png;base64, ' + base64.b64encode(f.read()).decode('ascii')

        return png_str


    def fix_zero(self, img_array):
        """
        Shift all values so that the minimum becomes zero.
        """
        img_array -= np.min(img_array)
        return self


    def corr_plane(self, img_array):
        """
        Correct the image by subtracting a fitted 2D-plane on the data
        """
        return SPM.SPM_image(BIN=img_array).correct_plane()


    def corr_median_diff(self, img_array):
        """
        Correct the image with the median difference
        """
        return SPM.SPM_image(BIN=img_array).correct_median_diff()


    def corr_slope(self, img_array):
        """
        Correct the image by subtracting a fitted slope along the y-axis
        """
        return SPM.SPM_image(BIN=img_array).correct_slope()


    def corr_lines(self, img_array):
        """
        Subtract the average of each line for the image.
        """
        return SPM.SPM_image(BIN=img_array).correct_lines()


    def corr_fit2d(self, img_array, nx=2, ny=2):
        """
        Subtract a fitted 2D-polynom of nx and ny order from the data
        Parameters
        ----------
        nx : int
            the polynom order for the x-axis
        ny : int
            the polynom order for the y-axis
        poly : bool
            if True the polynom is returned as output
        from https://github.com/scholi/pySPM/blob/master/pySPM/SPM.py
        index: 0 for image nr. 1, etc.
        """
        return SPM.SPM_image(BIN=img_array).corr_fit2d(nx=nx, ny=ny)
