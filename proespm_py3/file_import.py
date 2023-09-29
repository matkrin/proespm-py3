from __future__ import annotations
from typing import List, Tuple, TYPE_CHECKING
import os
import re
from dateutil import parser
import datetime

if TYPE_CHECKING:
    from rich.console import Console


ALLOWED_FTYPES = (
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
    ".lvm",
)


def import_files_folder_mode(files_dir: str, c: Console) -> List[str]:
    """Imports all files in a folder if filetype is supported

    Args:
        files_dir (str): Full path to the directory, containing the data files
            to import
        c (rich.Console): Console object for logging

    Returns:
        List[str]: List of full paths to imported files to process

    """
    c.log("[bold]Folder-based Mode[/bold]")
    file_lst = []  # full paths
    for entry in os.scandir(files_dir):
        if entry.path.endswith(ALLOWED_FTYPES) and entry.is_file():
            file_lst.append(entry.path)
            c.log(
                "Detected"
                f" File:\t\t[green]{os.path.basename(entry.path)}[/green]"
            )
        elif not entry.path.endswith(ALLOWED_FTYPES) and entry.is_file():
            c.log(
                f"Unsupported File:\t[red]{os.path.basename(entry.path)}[/red]"
            )
        elif not entry.is_file():
            c.log(
                f"Ignored Folder:\t\t[red]{os.path.basename(entry.path)}[/red]"
            )

    return file_lst


def prompt_date(c: Console) -> datetime.datetime:
    """Ask the user to enter a date

    The default date if the user just presses return is the actual day.

    Args:
        c (rich.Console): Console object for logging

    Return:
        datetime.datetime: The parsed date

    """
    today = datetime.datetime.today()
    date = input(f"Processing data for day (yyyy-mm-dd): [{today.date()}] ")
    if date == "":
        return today
    try:
        return parser.parse(date)
    except parser.ParserError:
        c.log("Not a valid date!")
        return prompt_date(c)


def import_files_day_mode(
    files_dir: str, c: Console
) -> Tuple[List[str], datetime.datetime]:
    """Searches recursively in folder to import files that match a given day

    Args:
        files_dir (str): Full path to the directory, to search in
        c (rich.Console): Console object for logging

    Returns:
        file_lst (List[str]): List of full paths to imported files
        date (datetime.datetime): The specified date

    """
    c.log("[bold]Day-based Mode[/bold]")
    date = prompt_date(c)
    date_regex = re.compile(
        r"([0-9]{4})-?(1[0-2]|0[1-9])-?(3[01]|0[1-9]|[12][0-9])"
    )
    file_lst: List[str] = []
    for dirpath, _, files in os.walk(files_dir):
        for f in files:
            if f.endswith((".mul", ".vms", ".png")):
                match = date_regex.search(f)
                if (
                    match is not None
                    and date.date() == parser.parse(match.group()).date()
                ):
                    file_lst.append(os.path.join(dirpath, f))
                else:
                    continue

    if file_lst == []:
        c.log(f"No files found for {date.date()}")
        return import_files_day_mode(files_dir, c)
    else:
        return file_lst, date
