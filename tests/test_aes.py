from pathlib import Path
from proespm.spectroscopy.aes_staib import AesStaib

testdata = Path(__file__).parent / "testdata"

AES_DAT = testdata / "aes-staib-dat.dat"
AES_VMS = testdata / "aes-staib-vms.vms"


def test_aes():
    parsed = AesStaib(str(AES_DAT))
    assert isinstance(parsed, AesStaib)
    parsed = AesStaib(str(AES_VMS))
    assert isinstance(parsed, AesStaib)


def test_aes_dat():
    aes = AesStaib(str(AES_DAT))
    assert aes.mode == "LockIn"
    assert aes.e_start
    assert round(aes.e_start) == 30
    assert aes.e_stop
    assert round(aes.e_stop) == 570
    assert aes.stepwidth
    assert round(aes.stepwidth) == 1
    assert aes.scan_num == 20
    assert aes.dwell_time == 123
    assert aes.retrace_time == 500
    assert aes.res == 20.0
    assert aes.res_mode == "dE/E=const."


def test_aes_vms():
    aes = AesStaib(str(AES_VMS))
    assert aes.mode == "analogue"
    assert aes.e_start
    assert round(aes.e_start) == 20
    assert aes.e_stop
    assert round(aes.e_stop) == 2200
    assert aes.stepwidth
    assert round(aes.stepwidth) == 2
    assert aes.scan_num == 1
    assert aes.dwell_time == 0.503
    assert aes.retrace_time == 5000
    assert aes.res == 1.0
    assert aes.res_mode == 1.0
