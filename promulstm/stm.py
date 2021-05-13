import numpy as np
import os
import scipy.optimize
import base64
import datetime
import matplotlib.pyplot as plt
plt.rcParams.update({'figure.max_open_warning': 0})
from matplotlib import transforms
from matplotlib_scalebar.scalebar import ScaleBar
from mul import Mul


class Stm:

    def __init__(self, img_dict):
        for key in img_dict:
            setattr(self, key, img_dict[key])
        """
        self.filename
        self.img_id
        self.img_num
        self.size
        self.xres
        self.yres
        self.zres
        self.datetime
        self.xsize
        self.ysize
        self.xoffset
        self.yoffset
        self.zscale
        self.tilt
        self.speed
        self.line_time
        self.bias
        self.current
        self.sample_string
        self.title_string
        self.postpr
        self.postd1
        self.mode
        self.currfac
        self.num_pointscans
        self.unitnr
        self.version
        self.gain
        self.img_data
        """


    def plot(self, dirc, save=False, show=False):
        """
        Plot the image.
        """
        fig, ax = plt.subplots(figsize=(5,5))
        ax.imshow(self.img_data*0.1,   #in nm
                   cmap='inferno',
                   vmin=None,
                   vmax=None,
                   origin='lower',
                   extent=(0, self.xsize*0.1,
                           0, self.ysize*0.1) #in nm
                 )
        #plt.colorbar()
        scalebar = ScaleBar(1,
                            "nm",
                            length_fraction=0.3,
                            location='lower right',
                            color='white',
                            box_alpha=0
                           )
        ax.add_artist(scalebar)
        ax.tick_params(left=False,
                       bottom=False,
                       labelleft=False,
                       labelbottom=False
                      )
        plt.tight_layout()

        if save is True:
            png_dir = os.path.join(dirc, self.filename.split('.')[0] + "_png")
            if not os.path.exists(png_dir):
                os.makedirs(png_dir)
            extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
            plt.savefig(os.path.join(png_dir, self.img_id +'.png'),
                        bbox_inches=extent
                       )
        if show is True:
            plt.show()
        return fig


    def add_png(self, dirc):
        """
        adds the png encoded string to the image dictionary when save=True
        for plot
        base64 encode: encodes png to bytes type
        decode: makes a string out of byte type
        """
        png_dir = os.path.join(dirc, self.filename.split('.')[0] + "_png")
        with open(os.path.join(png_dir, self.img_id + ".png"), 'rb') as f:
            self.png_str = 'data:image/png;base64, ' + base64.b64encode(f.read()).decode('ascii')


    def fix_zero(self):
        """
        Shift all values so that the minimum becomes zero.
        """
        self.img_data -= np.min(self.img_data)
        return self



    def corr_plane(self):
        """
        Subtract the average of each line for the image.
        if inline is True the current data are updated otherwise a new image
        with the corrected data is returned
        from https://github.com/scholi/pySPM/blob/master/pySPM/SPM.py
        index: 0 for image nr. 1, etc. 
        """
        x0, y0 = np.meshgrid(np.arange(self.xres), np.arange(self.yres))
        z0 = self.img_data
        x, y, z = x0, y0, z0
        a = np.column_stack((np.ones(z.ravel().size), x.ravel(), y.ravel()))
        c, resid, rank, sigma = np.linalg.lstsq(a, z.ravel(), rcond=-1)
        self.img_data -= c[0] * np.ones(self.img_data.shape) \
                         + c[1] * x0 + c[2] * y0
        return self


    def corr_median_diff(self):
        """
        Correct the image with the median difference
        from https://github.com/scholi/pySPM/blob/master/pySPM/SPM.py
        index: 0 for image nr. 1, etc. 
        """
        n = self.img_data
        n2 = n-np.vstack([n[:1, :],n[:-1, :]])
        c = np.cumsum(np.median(n2, axis=1))
        d = np.tile(c, (n.shape[0], 1)).T
        self.img_data = n-d
        return self


    def corr_slope(self):
        """
        Correct the image by subtracting a fitted slope along the y-axis
        from https://github.com/scholi/pySPM/blob/master/pySPM/SPM.py
        index: 0 for image nr. 1, etc. 
        """
        s = np.mean(self.img_data, axis=1)
        i = np.arange(len(s))
        fit = np.polyfit(i, s, 1)
        self.img_data -= np.tile(np.polyval(fit, i).reshape(len(i), 1), len(i))
        return self


    def corr_lines(self):
        """
        Subtract the average of each line for the image.
        if inline is True the current data are updated otherwise a new image 
        with the corrected data is returned
        from https://github.com/scholi/pySPM/blob/master/pySPM/SPM.py
        index: 0 for image nr. 1, etc. 
        """
        self.img_data -= np.tile(np.mean(self.img_data, axis=1).T,
                                 (self.img_data.shape[0], 1)).T
        return self


    def corr_fit2d(self, nx=2, ny=1):
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
        x = np.arange(self.img_data.shape[1], dtype=np.float)
        y = np.arange(self.img_data.shape[0], dtype=np.float)
        X0, Y0 = np.meshgrid(x, y)
        X, Y = X0, Y0
        Z = self.img_data
        x2 = X.ravel()
        y2 = Y.ravel()
        A = np.vstack([x2**i for i in range(nx+1)])
        A = np.vstack([A]+[y2**i for i in range(1, ny+1)])
        res = scipy.optimize.lsq_linear(A.T, Z.ravel())
        r = res['x']
        Z2 = r[0]*np.ones(self.img_data.shape)
        for i in range(1, nx+1):
            Z2 += r[i]*(X0**i)
        for i in range(1, ny+1):
            Z2 += r[nx+i]*(Y0**i)
        self.img_data -= Z2
        return self
