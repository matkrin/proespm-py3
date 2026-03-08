from pathlib import Path

from proespm.fastspm.atom_tracking import AtomTracking
from proespm.fastspm.error_topography import ErrorTopography
from proespm.fastspm.fast_scan import FastScan
from proespm.fastspm.high_speed import HighSpeed
from proespm.fastspm.slow_image import SlowImage


testdata = Path(__file__).parent / "testdata"

AT = testdata / "fastspm" / "AT_250526_002.h5"
ET = testdata / "fastspm" / "ET_250521_001.h5"
FS = testdata / "fastspm" / "FS_251120_001.h5"
HS = testdata / "fastspm" / "HS_250903_001.h5"
# RF = testdata / "fastspm" / "250526_003.txt"
SI = testdata / "fastspm" / "SI_250605_012.h5"


def test_atom_tracking():
    at = AtomTracking(AT)
    assert round(at.aux_1, 2) == -2.23
    assert at.aux_1_unit == "V/V"
    assert at.aux_1_label == "Bias"
    assert round(at.aux_2, 2) == -22.26
    assert at.aux_2_unit == "nA/V"
    assert at.aux_2_label == "Setpoint"


def test_atom_tracking_par():
    par = AtomTracking(AT).par
    assert par["E_WE_V"] == "-0.203 V"
    assert par["I_WE_A"] == "+1.816E-8 A"
    assert par["U_Tun_res_V"] == "+0.304 V"
    assert par["I_Tip_A"] == "-6.905E-11 A"
    assert par["U_Tip_V"] == "-0.508 V"


def test_error_topography():
    et = ErrorTopography(ET)
    assert round(et.aux_1, 2) == -2.23
    assert et.aux_1_unit == "V/V"
    assert et.aux_1_label == "Bias"
    assert round(et.aux_2, 2) == -22.26
    assert et.aux_2_unit == "nA/V"
    assert et.aux_2_label == "Setpoint"


def test_fast_scan():
    fs = FastScan(FS)
    assert fs.aux_1_unit == "V"
    assert fs.aux_1_label == "U_tun_res"
    assert round(fs.aux_2, 2) == -2.18
    assert fs.aux_2_unit == "nA"
    assert fs.aux_2_label == "Setpoint"


def test_high_speed():
    hs = HighSpeed(HS)
    assert hs.aux_1_unit == "V/V"
    assert hs.aux_1_label == "U_tun_res"
    assert round(hs.aux_2, 2) == -0.79
    assert hs.aux_2_unit == "nA/V"
    assert hs.aux_2_label == "Setpoint"


def test_slow_image():
    si = SlowImage(SI)
    assert si.aux_1_unit == "V/V"
    assert si.aux_1_label == "Bias"
    assert round(si.aux_2, 2) == -22.26
    assert si.aux_2_unit == "nA/V"
    assert si.aux_2_label == "Setpoint"
