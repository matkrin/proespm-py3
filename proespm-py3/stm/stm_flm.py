import datetime
from .stm_mul import StmMul
import os
import cv2

for k, v in os.environ.items():
    if k.startswith("QT_") and "cv2" in v:
        del os.environ[k]


class StmFlm(StmMul):
    """Class for handling Specs Aarhus STM .flm files

    Args:
        filepath (str): Full path to the .flm file

    """

    def __init__(self, filepath):
        super().__init__(filepath)

        self.m_id = self.filename
        self.mp4_save_dir = os.path.join(self.dirname, "movies")
        self.mp4_name = os.path.join(self.mp4_save_dir, f"{self.filename}.mp4")
        self.datetime = datetime.datetime.utcfromtimestamp(
            os.path.getmtime(filepath)
        )

    def convert_to_mp4(self, fps=10):
        """
        takes image-data(np-arrays) of all images in flm-file,
        flips the matrices vertically(as scanning starts in lower left corner),
        normalizes them from 0 to 255 and outputs them as mp4-file
        """
        dimensions = self.data[0].img_data.shape
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        output = os.path.join(self.mp4_save_dir, self.filename)

        if not os.path.exists(self.mp4_save_dir):
            os.makedirs(self.mp4_save_dir)

        video = cv2.VideoWriter(f"{output}.mp4", fourcc, fps, dimensions)

        scan_duration = 0
        for frame, img in enumerate(self.data):
            img_norm = cv2.normalize(
                img.img_data.arr,
                None,
                255,
                0,
                norm_type=cv2.NORM_MINMAX,
                dtype=cv2.CV_8U,
            )
            img_color = cv2.applyColorMap(img_norm, cv2.COLORMAP_HOT)

            overlay = img_color.copy()
            scan_duration += img.speed
            size = f"{img.xsize:.0f}nm x {img.ysize:.0f}nm"
            cv2.putText(
                overlay,
                f"{frame}, {scan_duration:.2f} s, {size}",
                (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (255, 255, 255, 0.1),
                1,
            )
            cv2.addWeighted(overlay, 0.5, img_color, 0.5, 0, img_color)
            video.write(img_color)

        video.release()
