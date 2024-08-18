import base64
import os
from datetime import datetime
from typing import Self

from prosurf.fileinfo import Fileinfo
from prosurf.labjournal import Labjournal


class Image:
    """Class handeling image files (.png, .jpg, .jpeg)"""
    ident = "IMAGE"

    def __init__(self, filepath: str) -> None:
        self.fileinfo = Fileinfo(filepath)

        self.m_id = self.fileinfo.filename
        self.labjournal_data: dict[str, str] | None = None
        self.datetime = datetime.fromtimestamp(os.path.getmtime(filepath))

        self.img_uri: str | None = None
        self.slide_num: int | None = None

    def encode_png(self):
        """Encodes an image to base64

        Returns:
            str: Data uri of the image
        """
        with open(self.fileinfo.filepath, "rb") as f:
            self.img_uri = (
                f"data:image/{self.fileinfo.fileext};base64, "
                + base64.b64encode(f.read()).decode("ascii")
            )

    def process(self) -> Self:
        self.encode_png()
        return self

    def set_labjournal_data(self, labjournal: Labjournal) -> None:
        self.labjournal_data = labjournal.extract_metadata_for_m_id(self.m_id)
