import os
from typing import final
from pathlib import Path


@final
class Fileinfo:
    """Class giving infos about a data file"""

    def __init__(self, filepath: Path) -> None:
        self.filepath = filepath
        self.basename = self.filepath.name
        self.dirname = self.filepath.parent
        self.filename, self.fileext = os.path.splitext(self.basename)
