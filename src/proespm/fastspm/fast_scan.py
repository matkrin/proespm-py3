from datetime import datetime, timezone
from typing import Self, final, override

import h5py

from proespm.config import Config
from proespm.fastspm.fastspm import read_corresponding_image, read_corresponding_par_file
from proespm.fileinfo import Fileinfo
from proespm.measurement import Measurement


@final
class FastScan(Measurement):
    """Class for handling .h5 files of fast scan (FS) measurements.

    Args:
        filepath (str): Full path to the .h5 file
    """

    op_mode = "FS"

    def __init__(self, filepath: str) -> None:
        self.fileinfo = Fileinfo(filepath)

        self.img_uri: str | None = None
        self.slide_num: int | None = None

        with h5py.File(filepath, mode="r") as f:
            self.attributes = dict(f["data"].attrs)

        self.aux_1 = float(self.attributes.get("Aux1.Value","0"))*float(self.attributes.get("Aux1.ConversionFactor","0")) * (2 * float(self.attributes.get("Aux1.InvertSignalIn","0")) - 1)
        self.aux_1_unit = self.attributes.get("Aux1.Unit","")
        self.aux_1_label = self.attributes.get("Aux1.Label","")

        self.aux_2 = float(self.attributes.get("Aux2.Value","0"))*float(self.attributes.get("Aux2.ConversionFactor","0")) * (2 * float(self.attributes.get("Aux2.InvertSignalIn","0")) - 1)
        self.aux_2_unit = self.attributes.get("Aux2.Unit","")
        self.aux_2_label = self.attributes.get("Aux2.Label","")

        self.scangain_x1 = self.attributes.get("Scanner.X1_Gain","")
        self.scangain_x2 = self.attributes.get("Scanner.X2_Gain","")
        self.scangain_y1 = self.attributes.get("Scanner.Y1_Gain ","")   # Spelling mistake in FastSPM .h5 file
        self.scangain_y2 = self.attributes.get("Scanner.Y2_Gain","")

        self.sig_in_convfact = float(self.attributes.get("Signal_In.ConversionFactor","nan"))
        self.sig_in_range = float(self.attributes.get("Signal_In.InputRange","nan"))
        self.sig_in_logamp = self.attributes.get("Signal_In.LogAmp","")
        self.sig_in_offset = float(self.attributes.get("Signal_In.Offset","nan"))
        self._sig_in_offset_unit = self.attributes.get("Signal_In.Offset.Unit","")
        self.sig_in_unit = self.attributes.get("Signal_In.Unit","")

        self.z_in_convfact = self.attributes.get("Z_In.ConversionFactor","")
        self.z_in_range = float(self.attributes.get("Z_In.InputRange","nan"))
        self.z_in_offset = float(self.attributes.get("Z_In.Offset","nan"))
        self.z_in_offset_unit = self.attributes.get("Z_In.Offset.Unit","")
        self.z_in_unit = self.attributes.get("Z_In.Unit","")

        self.temp_start = float(self.attributes.get("ExperimentInfo.TemperatureStart","nan"))
        self.temp_end = float(self.attributes.get("ExperimentInfo.TemperatureEnd","nan"))
        self.temp_unit = self.attributes.get("ExperimentInfo.Temperature.Unit","nan")

        self.frames_s = 2 * float(self.attributes.get("Scanner.Y_Frequency","nan"))
        self.frames_s_unit = self.attributes.get("Scanner.Y_Frequency.Unit","")

        self.x_frequency = float(self.attributes.get("Scanner.X_Frequency","nan"))
        self.x_frequency_unit = self.attributes.get("Scanner.X_Frequency.Unit","")

        self.px_frequency = float(self.attributes.get("Acquisition.ADC_SamplingRate","nan"))
        self.px_frequency_unit = self.attributes.get("Acquisition.ADC_SamplingRate.Units","")

        self.numframes = self.attributes.get("Acquisition.NumFrames","")

        self.scan_volt_x = float(self.attributes.get("Scanner.X_Amplitude","nan"))
        self.scan_volt_x_unit = self.attributes.get("Scanner.X_Amplitude.Unit","")
        self.scan_calib_x = float(self.attributes.get("Scanner.X_Calibration","nan"))
        self.scan_calib_x_unit = self.attributes.get("Scanner.X_Calibration.Unit","")
        self.scan_pnts_x = float(self.attributes.get("Scanner.X_Points","nan"))
        self.scan_volt_y = float(self.attributes.get("Scanner.Y_Amplitude","nan"))
        self.scan_volt_y_unit = self.attributes.get("Scanner.Y_Amplitude.Unit","")
        self.scan_calib_y = float(self.attributes.get("Scanner.Y_Calibration","nan"))
        self.scan_calib_y_unit = self.attributes.get("Scanner.Y_Calibration.Unit","")
        self.scan_pnts_y = float(self.attributes.get("Scanner.Y_Points","nan"))

        self.scan_size_unit = self.scan_calib_x_unit[:2] if self.scan_calib_x_unit.startswith(("nm","µm","mm","cm","m")) else ""

        self.x_phase = self.attributes.get("Acquisition.X_Phase","")
        self.x_phase_unit = self.attributes.get("Acquisition.X_Phase.Unit","")

        self.y_phase = self.attributes.get("Acquisition.Y_Phase","")
        self.y_phase_unit = self.attributes.get("Acquisition.Y_Phase.Unit","")

        self.angle = self.attributes.get("Scanner.Angle","")
        self.angle_unit = "°"

        self.par = read_corresponding_par_file(filepath)

    @override
    def m_id(self) -> str:
        return self.fileinfo.filename

    @override
    def datetime(self) -> datetime:
        time_start = self.attributes["ExperimentInfo.TimeStart"]  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
        assert isinstance(time_start, str)  # Type assertion

        return (
            datetime.fromisoformat(time_start)
            .astimezone(timezone.utc)
            .replace(tzinfo=None)
        )

    @override
    def process(self, config: Config) -> Self:
        self.img_uri = read_corresponding_image(self.fileinfo.filepath, False)
        return self

    @override
    def template_name(self) -> str:
        return "fastspm.j2"
