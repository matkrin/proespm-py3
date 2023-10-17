from __future__ import annotations
from typing import List, TYPE_CHECKING
import os
import sys
from jinja2 import Environment, FileSystemLoader


if TYPE_CHECKING:
    from proespm_py3.proespm_py3 import ExportObject
    from proespm_py3.proespm_py3 import DataObject


def check_type(data_obj: DataObject, check_str: str) -> bool:
    """Check if the name of the class data_obj instantiates from,
    matches check_str

    Used inside jinja templates as helper function as jinja does not support
    much python logic inside templated.

    Args:
        data_obj (DataObject): Object to check
        check_str (str): string to check

    Returns:
        bool: True if class name of data_obj matches check_str
    """

    return True if type(data_obj).__name__ == check_str else False


def create_html(
    data_objs: List[ExportObject], output_path: str, output_name: str
) -> None:
    """Creates the HTML report

    The list of data_objs get passed to the jinja environment and can be used
    inside of templates.

    Args:
        data_objs (list[DataObject]): list with DataObjects for the html report
        output_name (str): name or full path of the html report
    """

    if getattr(sys, "frozen", False):
        template_dir = os.path.join(sys._MEIPASS, "templates")  # type: ignore
    else:
        template_dir = os.path.join(os.path.dirname(__file__), "templates")

    env = Environment(loader=FileSystemLoader(template_dir))
    env.globals["check_type"] = check_type  # adds function to jinja env

    template = env.get_template("base_template.jinja")

    output = template.render(
        data_objs=data_objs,
        title=output_name,
        files_dir=output_path,
    )

    with open(f"{output_path}_report.html", "w", encoding="utf-8") as f:
        f.write(output)
