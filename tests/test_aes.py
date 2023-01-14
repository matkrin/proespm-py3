from pathlib import Path
from proespm_py3.aes import Aes

test_files = Path(__file__).parent / "test_files"

AES_DAT = test_files / "aes-staib-dat.dat"
AES_VMS = test_files / "aes-staib-vms.vms"

def test_aes():
    parsed = Aes(str(AES_DAT))
    assert isinstance(parsed, Aes)
    parsed = Aes(str(AES_VMS))
    assert isinstance(parsed, Aes)


def test_aes_dat():
    aes = Aes(str(AES_DAT))
    assert aes.mode == "LockIn"
    assert round(aes.e_start) == 30
    assert round(aes.e_stop) == 570
    assert round(aes.stepwidth) == 1
    assert aes.scan_num == 20
    assert aes.dwell_time == 123
    assert aes.retrace_time == 500
    assert aes.res == 20.0
    assert aes.res_mode == "dE/E=const."


def test_aes_vms():
    aes = Aes(str(AES_VMS))
    assert aes.mode == "analogue"
    assert round(aes.e_start) == 20
    assert round(aes.e_stop) == 2182
    assert round(aes.stepwidth) == 2
    assert aes.scan_num == 1
    assert aes.dwell_time == 0.503
    assert aes.retrace_time == 5000
    assert aes.res == 1.0
    assert aes.res_mode == 1.0
