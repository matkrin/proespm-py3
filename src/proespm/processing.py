import os
import sys
from pathlib import Path
from typing import Callable

from jinja2 import Environment, FileSystemLoader

from proespm.config import ALLOWED_FILE_TYPES, Config
from proespm.ec.ec4 import Ec4
from proespm.ec.ec_labview import CaLabview, CvLabview, FftLabview
from proespm.ec.PalmSens.ca import CaPalmSens
from proespm.ec.PalmSens.cp import CpPalmSens
from proespm.ec.PalmSens.cv import CvPalmSens
from proespm.ec.PalmSens.eis import EisPalmSens
from proespm.ec.PalmSens.lsv import LsvPalmSens
from proespm.ec.PalmSens.pssession import PalmSensSession
from proespm.measurement import Measurement
from proespm.misc.image import Image
from proespm.misc.qcmb import Qcmb
from proespm.misc.tpd import Tpd
from proespm.spectroscopy.aes_staib import AesStaib
from proespm.spectroscopy.xps_eis import XpsEis
from proespm.spm.flm import StmFlm
from proespm.spm.mtrx import StmMatrix
from proespm.spm.mul import StmMul
from proespm.spm.nid import SpmNid
from proespm.spm.sm4 import StmSm4
from proespm.spm.sxm import StmSxm


def check_file_for_str(file: str, string_to_check: str, line_num: int) -> bool:
    """Check if a file contains a string at a certain line number.

    Args:
        file: File to check.
        string_to_check: String to check for in `file`.
        line_num: Line number which is checked, starting from 1.

    Returns:
        True if `file` contains `string_to_check` at line `line_num`, False if not.
    """
    try:
        with open(file) as f:
            [next(f) for _ in range(line_num - 1)]
            line = f.readline()
        return string_to_check in line

    except Exception:
        with open(file, encoding="utf-16") as f:
            [next(f) for _ in range(line_num - 1)]
            line = f.readline()
        return string_to_check in line


def import_files(process_dir: str) -> list[str]:
    """Import files from a given directory and one level nested directories
    for processing.

    Args:
        process_dir: Full path of the directory containing files to import.

    Returns:
        List of full paths to imported files.
    """
    measurement_files: list[str] = []
    for entry in os.scandir(process_dir):
        if entry.is_dir():
            for sub_entry in os.scandir(entry):
                if sub_entry.is_file() and sub_entry.path.lower().endswith(
                    ALLOWED_FILE_TYPES
                ):
                    measurement_files.append(sub_entry.path)
        elif entry.is_file() and entry.path.lower().endswith(
            ALLOWED_FILE_TYPES
        ):
            measurement_files.append(entry.path)

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
    last_ec4: Ec4 | None = None

    measurement_objects: list[Measurement] = []
    for file_path in import_files(process_dir):
        path = Path(file_path)
        match path.suffix.lower():
            case ".z_mtrx":
                obj = StmMatrix(file_path)
                measurement_objects.append(obj)

            case ".mul":
                obj = StmMul(file_path)
                measurement_objects.append(obj)

            case ".sm4":
                obj = StmSm4(file_path)
                measurement_objects.append(obj)

            case ".sxm":
                obj = StmSxm(file_path)
                measurement_objects.append(obj)

            case ".nid":
                obj = SpmNid(file_path)
                measurement_objects.append(obj)

            case ".flm":
                obj = StmFlm(file_path)
                measurement_objects.append(obj)

            case ".vms" | ".dat":
                # TODO: check if vamas or dat file is really from Staib AES
                obj = AesStaib(file_path)
                measurement_objects.append(obj)

            case ".txt" if check_file_for_str(file_path, "Region", 1):
                obj = XpsEis(file_path)
                measurement_objects.append(obj)

            case ".txt" if check_file_for_str(file_path, "EC4 File", 1):
                obj = Ec4(file_path)
                if path.stem.endswith("1"):
                    last_ec4 = obj
                    measurement_objects.append(last_ec4)
                else:
                    assert last_ec4 is not None
                    last_ec4.push_cv_data(obj)

            case ".log":
                # TODO: check if valid qcmb file
                obj = Qcmb(file_path)
                measurement_objects.append(obj)

            case ".csv" if (
                not check_file_for_str(file_path, "Scan rate", 1)
                and not check_file_for_str(file_path, "Freq_Hz", 1)
                and not check_file_for_str(file_path, "Date and time", 1)
                and not check_file_for_str(file_path, "Date and time", 4)
            ):
                obj = CaLabview(file_path)
                measurement_objects.append(obj)

            case ".csv" if check_file_for_str(file_path, "Scan rate", 1):
                obj = CvLabview(file_path)
                measurement_objects.append(obj)

            case ".csv" if check_file_for_str(file_path, "Freq_Hz", 1):
                obj = FftLabview(file_path)
                measurement_objects.append(obj)

            case ".csv" if check_file_for_str(
                file_path, "Chronopotentiometry", 4
            ):
                obj = CpPalmSens(file_path)
                measurement_objects.append(obj)

            case ".csv" if check_file_for_str(
                file_path, "Chronoamperometry", 4
            ):
                obj = CaPalmSens(file_path)
                measurement_objects.append(obj)

            case ".csv" if check_file_for_str(
                file_path, "Cyclic Voltammetry", 4
            ):
                obj = CvPalmSens(file_path)
                measurement_objects.append(obj)

            case ".csv" if check_file_for_str(
                file_path, "Linear Sweep Voltammetry", 4
            ):
                obj = LsvPalmSens(file_path)
                measurement_objects.append(obj)

            case ".csv" if check_file_for_str(
                file_path, "Impedance Spectroscopy", 2
            ):
                obj = EisPalmSens(file_path)
                measurement_objects.append(obj)

            case ".png" | ".jpg" | ".jpeg":
                obj = Image(file_path)
                measurement_objects.append(obj)

            case ".lvm":
                obj = Tpd(file_path)
                measurement_objects.append(obj)

            case ".pssession":
                obj = PalmSensSession(file_path)
                measurement_objects.append(obj)

            case _:
                continue

    return measurement_objects


def process_loop(
    measurement_objects: list[Measurement],
    config: Config,
    log: Callable[[str], None],
) -> None:
    """Processing of `measurement_objects`.

    This basically sorts `measurement_objects` according to their `datetime` method
    and calls the `process` method on every `Measurement` object.
    For certain objects that contain image data, a running number is added that is
    used in the HTML report's modal.

    Args:
        measurement_objects: List of Objects that implement `Measurement` which
            are processed.
        config: Runtime configuration which contains information of user-selected
            options.
        log: Log function which is used to emit information about the processing
            status.
    """
    slide_num = 1
    measurement_objects.sort(key=lambda x: x.datetime())
    for measurement in measurement_objects:
        log(f"Processing of {measurement.m_id()}")
        _ = measurement.process(config)
        match measurement:
            case StmMatrix() | StmSm4() | StmSxm() | SpmNid() | Image():
                measurement.slide_num = slide_num
                slide_num += 1
            case StmMul() if type(measurement) is StmMul:
                for mul_image in measurement.mulimages:
                    mul_image.slide_num = slide_num  # pyright: ignore[reportAttributeAccessIssue]
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
        template_dir = os.path.join(sys._MEIPASS, "templates")  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType, reportAttributeAccessIssue]
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
