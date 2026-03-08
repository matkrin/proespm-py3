from pathlib import Path

from proespm.processing import _import_files, create_measurement_objs

testdata = Path(__file__).parent / "testdata"


def test_import_files():
    imported = _import_files(str(testdata))
    assert len(imported) == 43


def test_create_measurement_objs():
    measurement_objects = create_measurement_objs(str(testdata), lambda _: None)
    assert len(measurement_objects) == 50
