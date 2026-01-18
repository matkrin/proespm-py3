from pathlib import Path
from proespm.spm.nid import SpmNid

testdata = Path(__file__).parent / "testdata"

STM_FLM = testdata / "stm-aarhus-flm.flm"
STM_MUL_A = testdata / "stm-aarhus-mul-a.mul"
STM_MUL_B = testdata / "stm-aarhus-mul-b.mul"
STM_MATRIX = testdata / "20201111--4_1.Z_mtrx"
STM_RHK = testdata / "stm-rhk-sm4.SM4"
STM_NID = testdata / "stm-nanosurf-nid.nid"
AFM_NID = testdata / "afm-nanosurf-nid.nid"


def test_stm_nid():
    nid = SpmNid(str(STM_NID))
    assert nid.current == 1.00
    assert nid.bias == 600.0
    assert nid.xsize == 20.0
    assert nid.ysize == 20.0
    assert nid.xres == 256
    assert nid.yres == 256
    assert nid.rotation == 0.0
    assert nid.scan_duration == 51.20
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
    assert nid.rotation == 0.0
    assert round(nid.scan_duration, 2) == 254.98
    assert nid.line_time == 498.0
    assert nid.xoffset == 574.0
    assert nid.yoffset == -1200.0
