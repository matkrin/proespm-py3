import os
import sys
from pathlib import Path
from typing import Callable, TypeAlias

from jinja2 import Environment, FileSystemLoader

from proespm.ec.ec4 import Ec4
from proespm.ec.ec_labview import CaLabview, CvLabview, FftLabview
from proespm.ec.PalmSens.ca import CaPalmSens
from proespm.ec.PalmSens.cp import CpPalmSens
from proespm.ec.PalmSens.cv import CvPalmSens
from proespm.ec.PalmSens.eis import EisPalmSens
from proespm.ec.PalmSens.lsv import LsvPalmSens
from proespm.ec.PalmSens.pssession import PalmSensSession
from proespm.config import Config
from proespm.labjournal import Labjournal
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

ALLOWED_FILE_TYPES = (
    ".mul",
    ".z_mtrx",
    ".sm4",
    ".sxm",
    ".nid",
    ".flm",
    ".vms",
    ".txt",
    ".log",
    ".dat",
    ".csv",
    ".png",
    ".jpg",
    ".jpeg",
    ".lvm",
    ".pssession",
)

# TODO: make this a proper interface
ProcessObject: TypeAlias = (
    StmMatrix
    | StmMul
    | StmSm4
    | StmFlm
    | AesStaib
    | StmSxm
    | SpmNid
    | Qcmb
    | XpsEis
    | Ec4
    | CvLabview
    | CaLabview
    | FftLabview
    | Image
    | Tpd
    | CaPalmSens
    | CpPalmSens
    | CvPalmSens
    | EisPalmSens
    | LsvPalmSens
    | PalmSensSession
)


def check_file_for_str(file: str, string_to_check: str, line_num: int) -> bool:
    """Check if a file contains a string at a certain line number

    Args:
        file: File to check
        string_to_check: String that is checked if file contains it
        line_num: Line number which is checked, starting from 1

    Returns:
        True if file starts with string_to_check, False if not
    """
    try:
        with open(file) as f:
            [next(f) for _ in range(line_num - 1)]
            line = f.readline()
        return string_to_check in line
    except:
        with open(file, encoding="utf-16") as f:
            [next(f) for _ in range(line_num - 1)]
            line = f.readline()
        return string_to_check in line


def import_files(process_dir: str) -> list[str]:
    """Import files from a given directory that can be processed

    Args:
        process_dir: Full path of the directory containing files to import

    Returns:
        List of full paths to imported files
    """
    return sorted(
        [
            entry.path
            for entry in os.scandir(process_dir)
            if entry.path.lower().endswith(ALLOWED_FILE_TYPES)
            and entry.is_file()
        ],
        key=lambda x: os.path.getctime(x),
    )


def create_process_objs(
    process_dir: str, log: Callable[[str], None]
) -> list[ProcessObject]:
    """ """
    last_ec4: Ec4 | None = None

    process_objects: list[ProcessObject] = []
    for file_path in import_files(process_dir):
        path = Path(file_path)
        match path.suffix.lower():
            case ".z_mtrx":
                obj = StmMatrix(file_path)
                process_objects.append(obj)

            case ".mul":
                obj = StmMul(file_path)
                process_objects.append(obj)

            case ".sm4":
                obj = StmSm4(file_path)
                process_objects.append(obj)

            case ".sxm":
                obj = StmSxm(file_path)
                process_objects.append(obj)

            case ".nid":
                obj = SpmNid(file_path)
                process_objects.append(obj)

            case ".flm":
                obj = StmFlm(file_path)
                process_objects.append(obj)

            case ".vms" | ".dat":
                # TODO: check if vamas or dat file is really from Staib AES
                obj = AesStaib(file_path)
                process_objects.append(obj)

            case ".txt" if check_file_for_str(file_path, "Region", 1):
                obj = XpsEis(file_path)
                process_objects.append(obj)

            case ".txt" if check_file_for_str(file_path, "EC4 File", 1):
                obj = Ec4(file_path)
                if path.stem.endswith("1"):
                    last_ec4 = obj
                    process_objects.append(last_ec4)
                else:
                    assert last_ec4 is not None
                    last_ec4.push_cv_data(obj)

            case ".log":
                # TODO: check if valid qcmb file
                obj = Qcmb(file_path)
                process_objects.append(obj)

            case ".csv" if (
                not check_file_for_str(file_path, "Scan rate", 1)
                and not check_file_for_str(file_path, "Freq_Hz", 1)
                and not check_file_for_str(file_path, "Date and time", 1)
                and not check_file_for_str(file_path, "Date and time", 4)
            ):
                obj = CaLabview(file_path)
                process_objects.append(obj)

            case ".csv" if check_file_for_str(file_path, "Scan rate", 1):
                obj = CvLabview(file_path)
                process_objects.append(obj)

            case ".csv" if check_file_for_str(file_path, "Freq_Hz", 1):
                obj = FftLabview(file_path)
                process_objects.append(obj)

            case ".csv" if check_file_for_str(
                file_path, "Chronopotentiometry", 4
            ):
                obj = CpPalmSens(file_path)
                process_objects.append(obj)

            case ".csv" if check_file_for_str(
                file_path, "Chronoamperometry", 4
            ):
                obj = CaPalmSens(file_path)
                process_objects.append(obj)

            case ".csv" if check_file_for_str(
                file_path, "Cyclic Voltammetry", 4
            ):
                obj = CvPalmSens(file_path)
                process_objects.append(obj)

            case ".csv" if check_file_for_str(
                file_path, "Linear Sweep Voltammetry", 4
            ):
                obj = LsvPalmSens(file_path)
                process_objects.append(obj)

            case ".csv" if check_file_for_str(
                file_path, "Impedance Spectroscopy", 2
            ):
                obj = EisPalmSens(file_path)
                process_objects.append(obj)

            case ".png" | ".jpg" | ".jpeg":
                obj = Image(file_path)
                process_objects.append(obj)

            case ".lvm":
                obj = Tpd(file_path)
                process_objects.append(obj)

            case ".pssession":
                obj = PalmSensSession(file_path)
                process_objects.append(obj)

            case _:
                continue

    return process_objects


def process_loop(
    process_objects: list[ProcessObject],
    labjournal: Labjournal | None,
    config: Config,
    log: Callable[[str], None],
) -> None:
    """"""
    slide_num = 1
    process_objects.sort(key=lambda x: x.datetime)
    for x in process_objects:
        log(f"Processing of {x.m_id}")
        _ = x.process(config)
        if labjournal is not None:
            x.set_labjournal_data(labjournal)
        match x:
            case StmMatrix() | StmSm4() | StmSxm() | SpmNid() | Image():
                x.slide_num = slide_num
                slide_num += 1
            case StmMul():
                for mul_image in x.mulimages:
                    mul_image.slide_num = slide_num
                    slide_num += 1
            case _:
                pass


def create_html(
    process_objs: list[ProcessObject],
    labjournal: Labjournal | None,
    output_path: str,
    report_name: str,
) -> None:
    """Creates the HTML report

    The list of data_objs get passed to the jinja environment and can be used
    inside of templates.

    Args:
        process_objs: List with DataObjects for the html report
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
        process_objs=process_objs,
        labjournal=labjournal,
        title=report_name,
        files_dir=output_path.rstrip("_report.html"),
    )

    with open(output_path, "w", encoding="utf-8") as f:
        _ = f.write(output)
