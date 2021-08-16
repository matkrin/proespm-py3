import os
import cv2
for k, v in os.environ.items():
    if k.startswith("QT_") and "cv2" in v:
        del os.environ[k]
import datetime
import numpy as np
from stm import Stm
from stm_mul import Mul


class Flm(Mul, Stm):

    def __init__(self, filepath):
        self.filepath = filepath
        self.basename = os.path.basename(self.filepath)
        self.dirname = os.path.dirname(self.filepath)
        self.filename, self.fileext = os.path.splitext(self.basename)
        self.m_id = self.filename
        self.img_lst = self.read_mul(filepath)
        self.datetime = datetime.datetime.utcfromtimestamp(
            os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M:%S')


    def convert_to_mp4(self, fps=10):
        """
        takes image-data(np-arrays) of all images in flm-file,
        flips the matrices vertically(as scanning starts in lower left corner),
        normalizes them from 0 to 255 and outputs them as mp4-file
        """
        dimensions = self.img_lst[0]['img_data'].shape
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        output = os.path.splitext(self.filepath)[0]

        video = cv2.VideoWriter(f'{output}.mp4', fourcc, fps, dimensions)

        scan_duration = 0
        for frame, img in enumerate(self.img_lst):
            img_norm = cv2.normalize(img['img_data'], None, 255, 0,
                                     norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U
                                    )
            img_col = cv2.applyColorMap(img_norm, cv2.COLORMAP_HOT)

            overlay = img_col.copy()
            scan_duration += img['speed']
            size = f"{img['xsize']:.0f}nm x {img['ysize']:.0f}nm"
            cv2.putText(
                overlay,
                f"{frame}, {scan_duration:.2f} s, {size}",
                (10,20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (255,255,255,0.1),
                1,
            )

            cv2.addWeighted(overlay, 0.5, img_col, 0.5, 0, img_col)

            video.write(img_col)

        video.release()
