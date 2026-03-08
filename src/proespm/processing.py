import os
import sys
from pathlib import Path
from typing import Callable

from jinja2 import Environment, FileSystemLoader

from proespm.config import ALLOWED_FILE_TYPES, Config
from proespm.ec.ec_labview import CaLabview, CvLabview, FftLabview
from proespm.ec.nordic_ec4 import NordicEc4
from proespm.ec.PalmSens.ca import CaPalmSens
from proespm.ec.PalmSens.cp import CpPalmSens
from proespm.ec.PalmSens.cv import CvPalmSens
from proespm.ec.PalmSens.eis import EisPalmSens
from proespm.ec.PalmSens.lsv import LsvPalmSens
from proespm.ec.PalmSens.pssession import PalmSensSession
from proespm.fastspm.atom_tracking import AtomTracking
from proespm.fastspm.error_topography import ErrorTopography
from proespm.fastspm.fast_scan import FastScan
from proespm.fastspm.high_speed import HighSpeed
from proespm.fastspm.resonance_frequency import ResonanceFrequency
from proespm.fastspm.slow_image import SlowImage
from proespm.measurement import Measurement
from proespm.misc.elab_ftw import extract_elabftw
from proespm.misc.image import Image
from proespm.misc.qcmb import Qcmb
from proespm.misc.rga import RgaMassScan, RgaTimeSeries
from proespm.misc.tpd import Tpd
from proespm.spectroscopy.aes_staib import AesStaib
from proespm.spectroscopy.xps_eis import XpsEis
from proespm.spm.flm import StmFlm
from proespm.spm.mtrx import StmMatrix
from proespm.spm.mul import StmMul
from proespm.spm.nid import SpmNid
from proespm.spm.sm4 import StmSm4
from proespm.spm.sxm import StmSxm


def _check_file_for_str(
    file: Path, string_to_check: str, line_num: int
) -> bool:
    """Check if a file contains a string at a certain line number.

    Args:
        file: File to check.
        string_to_check: String to check for in `file`.
        line_num: Line number which is checked, starting from 1.

    Returns:
        True if `file` contains `string_to_check` at line `line_num`, False if not.
    """
    try:
        with file.open() as f:
            [next(f) for _ in range(line_num - 1)]
            line = f.readline()

    except UnicodeDecodeError:
        with file.open(encoding="utf-16") as f:
            [next(f) for _ in range(line_num - 1)]
            line = f.readline()

    return string_to_check in line


def _import_files(process_dir: str) -> list[Path]:
    """Import files from a given directory and one level nested directories
    for processing.

    Args:
        process_dir: Full path of the directory containing files to import.

    Returns:
        List of full paths to imported files.
    """
    measurement_files: list[Path] = []
    for entry in os.scandir(process_dir):
        if entry.is_dir():
            for sub_entry in os.scandir(entry):
                if sub_entry.is_file() and sub_entry.path.lower().endswith(
                    ALLOWED_FILE_TYPES
                ):
                    measurement_files.append(Path(sub_entry.path))

        elif entry.is_file() and entry.path.lower().endswith(
            ALLOWED_FILE_TYPES
        ):
            measurement_files.append(Path(entry.path))

    return sorted(measurement_files, key=lambda x: os.path.getctime(x))


def create_measurement_objs(
    process_dir: str, _log: Callable[[str], None]
) -> list[Measurement]:
    """Instantiation of `Measurement` objects.

    Every filepath entry in `process_dir` gets tested to uniquely identify its
    type of measurement and transformed into an object that implements
    `Measurement` accordingly.

    Args:
        process_dir: Full path of the directory containing files to import.

    Returns:
        List of `Measurement` objects derived from files at `process_dir`.
    """
    last_ec4: NordicEc4 | None = None

    measurement_objects: list[Measurement] = []
    for path in _import_files(process_dir):
        check = lambda s, n: _check_file_for_str(path, s, n)  # noqa: E731
        match path.suffix.lower():
            case ".z_mtrx":
                obj = StmMatrix(path)

            case ".mul":
                obj = StmMul(path)

            case ".sm4":
                obj = StmSm4(path)

            case ".sxm":
                obj = StmSxm(path)

            case ".nid":
                obj = SpmNid(path)

            case ".flm":
                obj = StmFlm(path)

            # case ".vms" if _check_file_for_str(file_path, "Staib SuperCMA", 3):
            case ".vms" if check("Staib SuperCMA", 3):
                obj = AesStaib(path)

            case ".dat" if check("AES", 3):
                obj = AesStaib(path)

            case ".txt" if check("Region", 1):
                obj = XpsEis(path)

            case ".txt" if check("EC4 File", 1):
                obj = NordicEc4(path)
                if path.stem.endswith("1"):
                    last_ec4 = obj
                    measurement_objects.append(last_ec4)
                else:
                    assert last_ec4 is not None
                    last_ec4.push_cv_data(obj)

                continue

            case ".txt" if check("Residual Gas Analyzer Software", 2) and check(
                "Analog Scan Setup:", 5
            ):
                obj = RgaMassScan(path)

            case ".txt" if check("Residual Gas Analyzer Software", 2) and check(
                "Pressure vs Time Scan Setup:", 5
            ):
                obj = RgaTimeSeries(path)

            case ".log" if check("Rate (Å/s)", 2):
                obj = Qcmb(path)

            case ".csv" if (
                not check("Scan rate", 1)
                and not check("Freq_Hz", 1)
                and not check("Date and time", 1)
                and not check("Date and time", 4)
            ):
                obj = CaLabview(path)

            case ".csv" if check("Scan rate", 1):
                obj = CvLabview(path)

            case ".csv" if check("Freq_Hz", 1):
                obj = FftLabview(path)

            case ".csv" if check("Chronopotentiometry", 4):
                obj = CpPalmSens(path)

            case ".csv" if check("Chronoamperometry", 4):
                obj = CaPalmSens(path)

            case ".csv" if check("Cyclic Voltammetry", 4):
                obj = CvPalmSens(path)

            case ".csv" if check("Linear Sweep Voltammetry", 4):
                obj = LsvPalmSens(path)

            case ".csv" if check("Impedance Spectroscopy", 2):
                obj = EisPalmSens(path)

            case ".png" | ".jpg" | ".jpeg" if not path.with_suffix(
                ".h5"
            ).exists():
                if path.name.startswith("RF"):
                    obj = ResonanceFrequency(path)
                else:
                    obj = Image(path)

            case ".lvm":
                obj = Tpd(path)

            case ".pssession":
                obj = PalmSensSession(path)

            case ".h5":
                if path.name.startswith("FS"):
                    obj = FastScan(path)
                elif path.name.startswith("AT"):
                    obj = AtomTracking(path)
                elif path.name.startswith("ET"):
                    obj = ErrorTopography(path)
                elif path.name.startswith("SI"):
                    obj = SlowImage(path)
                elif path.name.startswith("HS"):
                    obj = HighSpeed(path)
                else:
                    continue

            case ".json":
                objs = extract_elabftw(path)
                measurement_objects += objs
                continue

            case _:
                continue

        measurement_objects.append(obj)

    return measurement_objects


def process_loop(
    measurement_objects: list[Measurement],
    config: Config,
    log: Callable[[str], None],
) -> None:
    """Processing of `measurement_objects`.

    This basically sorts `measurement_objects` according to their `get_datetime` method
    and calls the `process` method on every `Measurement` object.
    For certain objects that contain image data, a running number is added that is
    used in the HTML report's image modal.

    Args:
        measurement_objects: List of Objects that implement `Measurement` which
            are processed.
        config: Runtime configuration which contains information of user-selected
            options.
        log: Log function which is used to emit information about the processing
            status.
    """
    slide_num = 1
    measurement_objects.sort(key=lambda x: x.get_datetime())
    for measurement in measurement_objects:
        log(f"Processing of {measurement.m_id()}")
        _ = measurement.process(config)
        match measurement:
            case (
                StmMatrix()
                | StmSm4()
                | StmSxm()
                | SpmNid()
                | Image()
                | FastScan()
                | AtomTracking()
                | ErrorTopography()
                | SlowImage()
                | HighSpeed()
                | ResonanceFrequency()
            ):
                measurement.slide_num = slide_num
                slide_num += 1
            case StmMul() if type(measurement) is StmMul:
                for mul_image in measurement.mulimages:
                    mul_image.slide_num = slide_num  # ty:ignore[unresolved-attribute]
                    slide_num += 1
            case _:
                pass


def create_html(
    measurement_objects: list[Measurement],
    output_path: str,
    report_name: str,
) -> None:
    """Creation of the HTML report.

    The list of data_objs get passed to the jinja environment and can be used
    inside of templates.

    Args:
        measurement_objects: List with DataObjects for the html report
        output_path: Full path where the report will be saved
        report_name: Name of the report
    """

    if getattr(sys, "frozen", False):
        template_dir = os.path.join(sys._MEIPASS, "templates")  # ty:ignore[unresolved-attribute]
    else:
        template_dir = os.path.join(os.path.dirname(__file__), "templates")

    env = Environment(loader=FileSystemLoader(template_dir))

    template = env.get_template("base_template.j2")

    output = template.render(
        measurement_objects=measurement_objects,
        title=report_name,
        files_dir=output_path.rstrip("_report.html"),
    )

    with open(output_path, "w", encoding="utf-8") as f:
        _ = f.write(output)
