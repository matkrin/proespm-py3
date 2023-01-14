from pathlib import Path
import proespm_py3.stm as stm
from proespm_py3.stm.stm_flm import StmFlm
from proespm_py3.stm.stm_mul import StmMul
from proespm_py3.stm.stm_matrix import StmMatrix
from proespm_py3.stm.stm_sm4 import StmSm4

test_files = Path(__file__).parent / "test_files"

STM_FLM = test_files / "stm-aarhus-flm.flm"
STM_MUL_A = test_files / "stm-aarhus-mul-a.mul"
STM_MUL_B = test_files / "stm-aarhus-mul-b.mul"
STM_MATRIX = test_files / "20201111--4_1.Z_mtrx"
STM_RHK = test_files / "stm-rhk-sm4.SM4"

def test_stm_factory():
    parsed = stm.stm_factory(str(STM_MUL_A))
    assert isinstance(parsed, StmMul)
    parsed = stm.stm_factory(str(STM_MUL_B))
    assert isinstance(parsed, StmMul)
    parsed = stm.stm_factory(str(STM_FLM))
    assert isinstance(parsed, StmFlm)
    parsed = stm.stm_factory(str(STM_MATRIX))
    assert isinstance(parsed, StmMatrix)
    parsed = stm.stm_factory(str(STM_RHK))
    assert isinstance(parsed, StmSm4)


def test_stm_mul():
    mul = stm.stm_mul.StmMul(str(STM_MUL_A))
    assert isinstance(mul, StmMul)
    assert len(mul) == 4
    assert mul[0].current == 0.23
    assert round(mul[0].bias, 1) == 221.9
    assert mul[0].xsize == 100
    assert mul[0].ysize == 100
    assert mul[0].tilt == 0
    assert mul[0].xres == 512
    assert mul[0].yres == 512
    assert round(mul[0].speed, 2) == 77.32
    assert round(mul[0].line_time, 2) == 151.02
    assert mul[0].xoffset == 0
    assert mul[0].yoffset == 0
    assert mul[0].gain == 955
    assert mul[0].mode == 0

    assert mul[3].current == 0.65
    assert round(mul[3].bias, 1) == 292.7
    assert mul[3].xsize == 100
    assert mul[3].ysize == 100
    assert mul[3].tilt == 0
    assert mul[3].xres == 512
    assert mul[3].yres == 512
    assert round(mul[3].speed, 2) == 129.34
    assert round(mul[3].line_time, 2) == 252.62
    assert round(mul[3].xoffset, 2) == -673.20
    assert round(mul[3].yoffset, 2) == 580.30
    assert mul[3].gain == 955
    assert mul[3].mode == 0
