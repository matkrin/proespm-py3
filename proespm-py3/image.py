import base64
import os
import datetime


class Image:
    def __init__(self, filepath):
        self.filepath = filepath
        self.basename = os.path.basename(self.filepath)
        self.dirname = os.path.dirname(self.filepath)
        self.filename, self.fileext = os.path.splitext(self.basename)

        self.m_id = os.path.splitext(self.filename)[0]
        self.png_str = None
        self.encode_png()
        self.datetime = datetime.datetime.utcfromtimestamp(
            os.path.getmtime(filepath)
        )

    def encode_png(self):
        """
        adds the png encoded string to the image dictionary when save=True for plot
        base64 encode: encodes png to bytes type
        decode: makes a string out of byte type
        """
        for png_img in self.filepath:
            with open(self.filepath, "rb") as f:
                self.png_str = "data:image/png;base64, " + base64.b64encode(
                    f.read()
                ).decode("ascii")
        return self.png_str
