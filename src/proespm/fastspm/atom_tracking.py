import base64
from datetime import datetime, timezone
from pathlib import Path
from typing import Self, final, override

import h5py

from proespm.config import Config
from proespm.fileinfo import Fileinfo
from proespm.measurement import Measurement


IMAGE_EXTENSION = "jpg"


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

        self.x_amplitude = self.attributes["Circular_movement.X_Amplitude"]
        self.x_amplitude_unit = self.attributes[
            "Circular_movement.X_Amplitude.Unit"
        ]

        self.y_amplitude = self.attributes["Circular_movement.Y_Amplitude"]
        self.y_amplitude_unit = self.attributes[
            "Circular_movement.Y_Amplitude.Unit"
        ]

        self.rotation_phase = self.attributes[
            "Circular_movement.Rotation_Phase"
        ]
        self.rotation_phase_unit = self.attributes[
            "Circular_movement.Rotation_Phase.Unit"
        ]

        self.lockin_phase = self.attributes["LockIn.Phase"]
        # TODO: this is wierd
        self.lockin_phase_unit = self.attributes["LockIn.Phase.Unit"].encode(
            "utf8", "backslashreplace"
        )

        self.lockin_timeconstant = self.attributes["LockIn.TimeConstant"]
        self.lockin_timeconstant_unit = self.attributes[
            "LockIn.TimeConstant.Unit"
        ]

        self.k_p = self.attributes["PI.Kp"]
        self.k_p_unit = self.attributes["PI.Kp.Unit"]

        self.ti = self.attributes["PI.Ti"]
        self.ti_unit = self.attributes["PI.Ti.Unit"]

        self.control_timestep = self.attributes["PI.ControlTimeStep"]
        self.control_timestep_unit = self.attributes["PI.ControlTimeStep.Unit"]

        self.hardware = self.attributes["PI.Hardware"]

        self.circle_by_circle = self.attributes["PI.CircleByCircle"]
        self.num_circles = self.attributes["PI.CircleByCircle.Number"]

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
        with (
            Path(self.fileinfo.filepath)
            .with_suffix(f".{IMAGE_EXTENSION}")
            .open("rb") as image_file
        ):
            self.img_uri = (
                f"data:image/{IMAGE_EXTENSION};base64, "
                + base64.b64encode(image_file.read()).decode("ascii")
            )

        return self

    @override
    def template_name(self) -> str:
        return "fastspm.j2"


at = AtomTracking("/Users/matthias/Downloads/testdatanew/AT_250526_002.h5")
