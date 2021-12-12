import numpy as np
import os
import io
import base64
import datetime
import matplotlib.pyplot as plt
plt.rcParams.update({'figure.max_open_warning': 0})
from matplotlib import transforms
from matplotlib_scalebar.scalebar import ScaleBar
import seaborn as sns


class Stm:

    def plot(self, img_array, xsize, ysize, save_dir, save_name, save=False, show=False):
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

        png_bytes = io.BytesIO()
        extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
        plt.savefig(png_bytes, bbox_inches=extent)
        png_bytes.seek(0)
        png_str = 'data:image/png;base64, ' + base64.b64encode(png_bytes.read()).decode('ascii')

        if save is True:
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
            plt.savefig(os.path.join(save_dir, save_name + '.png'), bbox_inches=extent)

        if show is True:
            plt.show()
        return png_str


    def fix_zero(self, img_array):
        """
        Subtracts the minimum value of the image array from the image array
        """
        img_array -= np.min(img_array)
        return self


    def corr_lines(self, img_array):
        """
        Subtracts a plane of the average of each scan line from the image array
        """
        mean = np.mean(img_array, axis=1)
        correction = np.broadcast_to(mean, img_array.shape).T
        img_array -= correction
        return img_array


    def corr_plane(self, img_array):
        """
        Subtracts a fitted background plane from the image array
        """
        x_shape, y_shape = img_array.shape
        x_arr = np.broadcast_to(np.arange(x_shape), img_array.shape)
        y_arr = np.repeat(np.arange(y_shape), y_shape).reshape(img_array.shape)
        
        stack = np.column_stack(
            (np.ones(img_array.size), x_arr.flatten(), y_arr.flatten())
        ) 
        least_squares = np.linalg.lstsq(stack, img_array.flatten(), rcond=-1)[0]
        correction = (least_squares[0] * np.ones(img_array.shape)
               + least_squares[1] * x_arr
               + least_squares[2] * y_arr)
        img_array -= correction
        return img_array
