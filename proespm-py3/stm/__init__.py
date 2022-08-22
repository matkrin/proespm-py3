import os
import datetime

from .stm_mul import StmMul
from .stm_flm import StmFlm
from .stm_sm4 import StmSm4
from .stm_matrix import NoTracesError, StmMatrix
from .stm_sxm import StmSxm


class ErrorFile:
    def __init__(self, filepath):
        self.filepath = filepath
        self.basename = os.path.basename(self.filepath)
        self.dirname = os.path.dirname(self.filepath)
        self.filename, self.fileext = os.path.splitext(self.basename)
        self.datetime = datetime.datetime.utcfromtimestamp(
            os.path.getmtime(filepath)
        )


def stm_factory(file):
    if file.endswith(".mul"):
        return StmMul(file)
    elif file.endswith(".flm"):
        return StmFlm(file)
    elif file.endswith(".Z_mtrx"):
        try:
            return StmMatrix(file)
        except NoTracesError as e:
            print("An error occurred: ", e)
            return ErrorFile(file)
    elif file.endswith(".SM4"):
        return StmSm4(file)
    elif file.endswith(".sxm"):
        return StmSxm(file)
    pass
