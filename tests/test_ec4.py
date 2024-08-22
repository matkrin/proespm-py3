from pathlib import Path
from proespm.ec.ec4 import Ec4


testdata = Path(__file__).parent / "testdata"

CV_EC4 = testdata / r"CV_153505_ 1.txt"
CV_EC4_2 = testdata / r"CV_153605_ 2.txt"
LSV_EC4 = testdata / r"CV_185158_ 1.txt"
CA_EC4 = testdata / r"CV_103244_ 1.txt"
CA_EC4_2 = testdata / r"CV_103345_ 2.txt"


def test_cv_ec4():
    cv_ec4 = Ec4(str(CV_EC4))
    assert isinstance(cv_ec4, Ec4)
    assert cv_ec4.u_start == 0.800
    assert cv_ec4.u_1 == -0.400
    assert cv_ec4.u_2 == 1.100
    assert cv_ec4.rate == 0.050


def test_cv_ec4_2():
    cv_ec4 = Ec4(str(CV_EC4_2))
    assert isinstance(cv_ec4, Ec4)
    assert cv_ec4.u_start == 0.800
    assert cv_ec4.u_1 == -0.400
    assert cv_ec4.u_2 == 1.100
    assert cv_ec4.rate == 0.050


def test_lsv_ec4():
    lsv_ec4 = Ec4(str(LSV_EC4))
    assert isinstance(lsv_ec4, Ec4)
    assert lsv_ec4.u_start == 1.100
    assert lsv_ec4.u_1 == 1.100
    assert lsv_ec4.u_2 == 0.100
    assert lsv_ec4.rate == 0.005


def test_ca_ec4():
    ca_ec4 = Ec4(str(CA_EC4))
    assert isinstance(ca_ec4, Ec4)
    assert ca_ec4.u_start == 0.700
    assert ca_ec4.u_1 == -0.400
    assert ca_ec4.u_2 == 1.100
    assert ca_ec4.rate == 0.050


def test_ca_ec4_2():
    ca_ec4 = Ec4(str(CA_EC4_2))
    assert isinstance(ca_ec4, Ec4)
    assert ca_ec4.u_start == 0.700
    assert ca_ec4.u_1 == -0.400
    assert ca_ec4.u_2 == 1.100
    assert ca_ec4.rate == 0.050
