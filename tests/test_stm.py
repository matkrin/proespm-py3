from pathlib import Path
from proespm.spm.mul import StmMul
from proespm.spm.nid import SpmNid

testdata = Path(__file__).parent / "testdata"

STM_FLM = testdata / "stm-aarhus-flm.flm"
STM_MUL_A = testdata / "stm-aarhus-mul-a.mul"
STM_MUL_B = testdata / "stm-aarhus-mul-b.mul"
STM_MATRIX = testdata / "20201111--4_1.Z_mtrx"
STM_RHK = testdata / "stm-rhk-sm4.SM4"
STM_NID = testdata / "stm-nanosurf-nid.nid"
AFM_NID = testdata / "afm-nanosurf-nid.nid"

# def test_stm_mul():
#     mul = StmMul(str(STM_MUL_A)).mulimages
#     assert len(mul) == 4
#     assert mul[0].current == 0.23
#     assert round(mul[0].bias, 1) == 221.9
#     assert mul[0].xsize == 100
#     assert mul[0].ysize == 100
#     assert mul[0].tilt == 0
#     assert mul[0].xres == 512
#     assert mul[0].yres == 512
#     assert round(mul[0].speed, 2) == 77.32
#     assert round(mul[0].line_time, 2) == 151.02
#     assert mul[0].xoffset == 0
#     assert mul[0].yoffset == 0
#     assert mul[0].gain == 955
#     assert mul[0].mode == 0
#
#     assert mul[3].current == 0.65
#     assert round(mul[3].bias, 1) == 292.7
#     assert mul[3].xsize == 100
#     assert mul[3].ysize == 100
#     assert mul[3].tilt == 0
#     assert mul[3].xres == 512
#     assert mul[3].yres == 512
#     assert round(mul[3].speed, 2) == 129.34
#     assert round(mul[3].line_time, 2) == 252.62
#     assert round(mul[3].xoffset, 2) == -673.20
#     assert round(mul[3].yoffset, 2) == 580.30
#     assert mul[3].gain == 955
#     assert mul[3].mode == 0


def test_stm_nid():
    nid = SpmNid(str(STM_NID))
    assert nid.current == 1.00
    assert nid.bias == 600.0
    assert nid.xsize == 20.0
    assert nid.ysize == 20.0
    assert nid.xres == 256
    assert nid.yres == 256
    assert nid.tilt == 0.0
    assert nid.scan_duration == 25.60
    assert nid.line_time == 100.0
    assert nid.xoffset == -213.0
    assert nid.yoffset == -118.0


def test_afm_nid():
    nid = SpmNid(str(AFM_NID))
    assert nid.current == 70.00
    assert nid.bias == 0.0
    assert nid.xsize == 7000.0
    assert nid.ysize == 7000.0
    assert nid.xres == 256
    assert nid.yres == 256
    assert nid.tilt == 0.0
    assert round(nid.scan_duration, 2) == 127.49
    assert nid.line_time == 498.0
    assert nid.xoffset == 574.0
    assert nid.yoffset == -1200.0
