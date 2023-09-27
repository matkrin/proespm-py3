from pathlib import Path
from proespm_py3.aes import Aes
from proespm_py3.ec4 import Ec4
from proespm_py3.image import Image
from proespm_py3.proespm_py3 import datafile_factory, instantiate_data_objs
from proespm_py3.qcmb import Qcmb
from proespm_py3.stm.stm_matrix import StmMatrix
from proespm_py3.stm.stm_mul import StmMul
from proespm_py3.stm.stm_flm import StmFlm
from proespm_py3.stm.stm_nid import NanosurfNid
from proespm_py3.stm.stm_sm4 import StmSm4
from proespm_py3.xps import XpsEis


test_file_path = Path(__file__).parent / "test_files"

TEST_FILES = {
    "stm_flm": test_file_path / "stm-aarhus-flm.flm",
    "stm_mul_a": test_file_path / "stm-aarhus-mul-a.mul",
    "stm_mul_b": test_file_path / "stm-aarhus-mul-b.mul",
    "stm_matrix": test_file_path / "20201111--4_1.Z_mtrx",
    "stm_rhk": test_file_path / "stm-rhk-sm4.SM4",
    "stm_nid": test_file_path / "stm-nanosurf-nid.nid",
    "afm_nid": test_file_path / "afm-nanosurf-nid.nid",
    "aes_dat": test_file_path / "aes-staib-dat.dat",
    "aes_vms": test_file_path / "aes-staib-vms.vms",
    "leed_png": test_file_path / "leed.png",
    "qcmb_log": test_file_path / "qcmb-test.log",
    "xps_eis": test_file_path / "xps-eis.txt",
    "wrong_txt": test_file_path / "wrong-txt.txt",
    "cv_ec4": test_file_path / r"CV_153505_ 1.txt",
    "cv_ec4_2": test_file_path / r"CV_153605_ 2.txt",
    "lsv_ec4": test_file_path / r"CV_185158_ 1.txt",
    "ca_ec4": test_file_path / r"CV_103244_ 1.txt",
    "ca_ec4_2": test_file_path / r"CV_103345_ 2.txt",
}

def test_datafile_factory():
    data_obj = datafile_factory(str(TEST_FILES["stm_mul_a"]))
    assert data_obj is not None
    assert isinstance(data_obj, StmMul)

    data_obj = datafile_factory(str(TEST_FILES["stm_flm"]))
    assert data_obj is not None
    assert isinstance(data_obj, StmFlm)

    data_obj = datafile_factory(str(TEST_FILES["stm_matrix"]))
    assert data_obj is not None
    assert isinstance(data_obj, StmMatrix)

    data_obj = datafile_factory(str(TEST_FILES["stm_rhk"]))
    assert data_obj is not None
    assert isinstance(data_obj, StmSm4)

    data_obj = datafile_factory(str(TEST_FILES["stm_nid"]))
    assert data_obj is not None
    assert isinstance(data_obj, NanosurfNid)

    data_obj = datafile_factory(str(TEST_FILES["afm_nid"]))
    assert data_obj is not None
    assert isinstance(data_obj, NanosurfNid)

    data_obj = datafile_factory(str(TEST_FILES["aes_dat"]))
    assert data_obj is not None
    assert isinstance(data_obj, Aes)

    data_obj = datafile_factory(str(TEST_FILES["aes_vms"]))
    assert data_obj is not None
    assert isinstance(data_obj, Aes)

    data_obj = datafile_factory(str(TEST_FILES["leed_png"]))
    assert data_obj is not None
    assert isinstance(data_obj, Image)

    data_obj = datafile_factory(str(TEST_FILES["qcmb_log"]))
    assert data_obj is not None
    assert isinstance(data_obj, Qcmb)

    data_obj = datafile_factory(str(TEST_FILES["xps_eis"]))
    assert data_obj is not None
    assert isinstance(data_obj, XpsEis)

    data_obj = datafile_factory(str(TEST_FILES["wrong_txt"]))
    assert data_obj is None

    data_obj = datafile_factory(str(TEST_FILES["cv_ec4"]))
    assert isinstance(data_obj, Ec4)
    data_obj = datafile_factory(str(TEST_FILES["cv_ec4_2"]))
    assert isinstance(data_obj, Ec4)
    data_obj = datafile_factory(str(TEST_FILES["lsv_ec4"]))
    assert isinstance(data_obj, Ec4)
    data_obj = datafile_factory(str(TEST_FILES["ca_ec4"]))
    assert isinstance(data_obj, Ec4)
    data_obj = datafile_factory(str(TEST_FILES["ca_ec4_2"]))
    assert isinstance(data_obj, Ec4)


def test_instantiate_data_objs():
    data_objs = instantiate_data_objs([str(x) for x in TEST_FILES.values()])
    assert type(data_objs) == list
