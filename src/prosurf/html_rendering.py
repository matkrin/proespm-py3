from __future__ import annotations
import os
import sys
from typing import TYPE_CHECKING
from jinja2 import Environment, FileSystemLoader


if TYPE_CHECKING:
    from prosurf.main import ProcessObject


def create_html(
    process_objs: list[ProcessObject],
    output_path: str,
    output_name: str,
) -> None:
    """Creates the HTML report

    The list of data_objs get passed to the jinja environment and can be used
    inside of templates.

    Args:
        process_objs: list with DataObjects for the html report
        output_name:  name or full path of the html report
    """

    if getattr(sys, "frozen", False):
        template_dir = os.path.join(sys._MEIPASS, "templates")  # type: ignore[reportMissing]
    else:
        template_dir = os.path.join(os.path.dirname(__file__), "templates")

    env = Environment(loader=FileSystemLoader(template_dir))

    template = env.get_template("base_template.j2")

    output = template.render(
        process_objs=process_objs,
        title=output_name,
        files_dir=output_path,
    )

    with open(f"{output_path}_report.html", "w", encoding="utf-8") as f:
        _= f.write(output)
