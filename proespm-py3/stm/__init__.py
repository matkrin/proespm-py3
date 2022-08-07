from .stm_mul import StmMul
from .stm_flm import StmFlm
from .stm_sm4 import StmSm4
from .stm_matrix import StmMatrix
from .stm_sxm import StmSxm


def stm_factory(file):
    if file.endswith(".mul"):
        return StmMul(file)
    elif file.endswith(".flm"):
        return StmFlm(file)
    elif file.endswith(".Z_mtrx"):
        return StmMatrix(file)
    elif file.endswith(".SM4"):
        return StmSm4(file)
    elif file.endswith(".sxm"):
        return StmSxm(file)
    pass
