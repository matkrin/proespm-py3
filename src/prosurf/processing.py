import os
import sys
from typing import Callable, TypeAlias

from jinja2 import Environment, FileSystemLoader

from prosurf.spm.mtrx import StmMatrix
from prosurf.spm.mul import StmMul
from prosurf.spm.sm4 import StmSm4


ALLOWED_FILE_TYPES = (
    ".mul",
    ".png",
    ".txt",
    ".Z_mtrx",
    ".flm",
    ".log",
    ".SM4",
    ".dat",
    ".sxm",
    ".vms",
    ".nid",
    ".jpg",
    ".jpeg",
    ".csv",
)

ProcessObject: TypeAlias = StmMatrix | StmMul | StmSm4


def process_loop(
    process_dir: str, log: Callable[[str], None]
) -> list[ProcessObject]:
    """ """
    slide_num = 1
    processed: list[ProcessObject] = []
    for entry in os.scandir(process_dir):
        file_path = entry.path
        if file_path.endswith(ALLOWED_FILE_TYPES) and entry.is_file():
            log(f"Processing of {file_path}")
            if file_path.endswith(".Z_mtrx"):
                obj = StmMatrix(file_path)
                obj.process()
                obj.slide_num = slide_num
                slide_num += 1
                processed.append(obj)

            elif file_path.endswith(".mul"):
                obj = StmMul(file_path)
                obj.process()
                obj.slide_num = slide_num
                for mul_image in obj.mulimages:  # type: ignore[reportUnknownVariableType]
                    mul_image.slide_num = slide_num
                    slide_num += 1
                processed.append(obj)

            elif file_path.lower().endswith(".sm4"):
                obj = StmSm4(file_path)
                obj.process()
                obj.slide_num = slide_num
                slide_num += 1
                processed.append(obj)

    return processed


def create_html(
    process_objs: list[ProcessObject],
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
        template_dir = os.path.join(sys._MEIPASS, "templates")  # type: ignore[reportMissing]
    else:
        template_dir = os.path.join(os.path.dirname(__file__), "templates")

    env = Environment(loader=FileSystemLoader(template_dir))

    template = env.get_template("base_template.j2")

    output = template.render(
        process_objs=process_objs,
        title=report_name,
        files_dir=output_path.rstrip("_report.html"),
    )

    with open(output_path, "w", encoding="utf-8") as f:
        _ = f.write(output)
