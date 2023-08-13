import base64
import os
import datetime
from typing import Optional


class Image:
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.basename = os.path.basename(self.filepath)
        self.dirname = os.path.dirname(self.filepath)
        self.filename, self.fileext = os.path.splitext(self.basename)

        self.m_id = os.path.splitext(self.filename)[0]
        self.datetime = datetime.datetime.utcfromtimestamp(
            os.path.getmtime(filepath)
        )

        self.png_str = self.encode_png()
        self.slide_num: Optional[int] = None

    def encode_png(self) -> str:
        """Encodes an image to base64

        Returns:
            str: data uri of the image
        """
        with open(self.filepath, "rb") as f:
            png_str = "data:image/png;base64, " + base64.b64encode(
                f.read()
            ).decode("ascii")
        return png_str
