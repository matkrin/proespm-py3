from pathlib import Path

from proespm.misc.rga import RgaMassScan, RgaTimeSeries


testdata = Path(__file__).parent / "testdata"

RGA_MASSSCAN = testdata / "rga-massscan-test.txt"
RGA_TIMESERIES = testdata / "rga-timeseries-test.txt"


def test_rga_massscan():
    rga = RgaMassScan(str(RGA_MASSSCAN))
    assert rga.num_datapoints == 641
    assert rga.units == "Torr"
    assert rga.noise_floor == 2
    assert rga.cem_status == "ON"
    assert rga.points_per_amu == 10
    assert rga.data.shape == (641, 2)


def test_rga_timeseries():
    rga = RgaTimeSeries(str(RGA_TIMESERIES))
    assert rga.active_channels == 10
    assert rga.units == "Torr"
    assert rga.sample_period == 1.00
    assert rga.sample_period_unit == "sec"
    assert len(rga.channels) == 10
    assert rga.data.shape == (711, 11)
