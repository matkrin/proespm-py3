from datetime import datetime, timezone
from typing import Self, final, override

import h5py

from proespm.config import Config
from proespm.fastspm.fastspm import read_corresponding_image
from proespm.fileinfo import Fileinfo
from proespm.measurement import Measurement


@final
class AtomTracking(Measurement):
    """Class for handling .h5 files of atom tracking (AT) measurements.

    Args:
        filepath (str): Full path to the .h5 file
    """

    op_mode = "AT"

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
        self.scangain_y1 = self.attributes.get("Scanner.Y1_Gain","")
        self.scangain_y2 = self.attributes.get("Scanner.Y2_Gain","")

        self.sig_in_convfact = float(self.attributes.get("Signal_In.ConversionFactor","nan"))
        self.sig_in_logamp = self.attributes.get("Signal_In.LogAmp","")
        self.sig_in_offset = float(self.attributes.get("Signal_In.Offset","nan"))
        self._sig_in_offset_unit = self.attributes.get("Signal_In.Offset.Unit","")
        self.sig_in_unit = self.attributes.get("Signal_In.Unit","")

        self.z_in_convfact = float(self.attributes.get("Z_In.ConversionFactor","nan"))
        self.z_in_offset = float(self.attributes.get("Z_In.Offset","nan"))
        self.z_in_offset_unit = self.attributes.get("Z_In.Offset.Unit","")
        self.z_in_unit = self.attributes.get("Z_In.Unit","")

        self.temp_start = self.attributes.get("ExperimentInfo.TemperatureStart","nan")
        self.temp_end = self.attributes.get("ExperimentInfo.TemperatureEnd","nan")
        self.temp_unit = self.attributes.get("ExperimentInfo.Temperature.Unit","nan")

        self.x_amplitude = self.attributes.get("Circular_movement.X_Amplitude","")
        self.x_amplitude_unit = self.attributes.get("Circular_movement.X_Amplitude.Unit","")

        self.y_amplitude = self.attributes.get("Circular_movement.Y_Amplitude","")
        self.y_amplitude_unit = self.attributes.get("Circular_movement.Y_Amplitude.Unit","")

        self.rotation_phase = self.attributes.get("Circular_movement.Rotation_Phase","")
        self.rotation_phase_unit = "°"
        
        self.lockin_phase = self.attributes.get("LockIn.Phase","")
        self.lockin_phase_unit = "°"
        
        self.lockin_timeconstant = self.attributes.get("LockIn.TimeConstant","")
        self.lockin_timeconstant_unit = self.attributes.get("LockIn.TimeConstant.Unit","")

        self.k_p = self.attributes.get("PI.Kp","")
        self.k_p_unit = self.attributes.get("PI.Kp.Unit","")

        self.ti = self.attributes.get("PI.Ti","")
        self.ti_unit = self.attributes.get("PI.Ti.Unit","")

        self.control_timestep = self.attributes.get("PI.ControlTimeStep","")
        self.control_timestep_unit = self.attributes.get("PI.ControlTimeStep.Unit","")

        self.hardware = self.attributes.get("PI.Hardware","")

        self.circle_by_circle = self.attributes.get("PI.CircleByCircle","")
        self.num_circles = self.attributes.get("PI.CircleByCircle.Number","")

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
