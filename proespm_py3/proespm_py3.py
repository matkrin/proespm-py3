from typing import List, Union, Optional
import pandas as pd
import os
from rich.console import Console
from rich.progress import track, Progress
from rich import print
from mulfile.mul import MulImage

import config
from stm import (
    stm_factory,
    StmFlm,
    StmMatrix,
    StmMul,
    StmSm4,
    StmSxm,
    ErrorFile,
)
from image import Image
from xps import XpsEis, XpsScan
from aes import Aes
from qcmb import Qcmb
from file_import import import_files_day_mode, import_files_folder_mode
from gui import prompt_folder, prompt_labj
from html_rendering import create_html


DataObject = Union[
    StmMul,
    StmFlm,
    StmMatrix,
    StmSm4,
    StmSxm,
    ErrorFile,
    Image,
    XpsScan,
    XpsEis,
    Aes,
    Qcmb,
]

c = Console()  # normal logging
pc = Progress().console  # logging in loops with track()


def extract_labj(labjournal, obj):
    """extract data of a labjournal excel file"""

    try:
        matched_row = labjournal[labjournal["ID"].str.match(obj.m_id)]
        row_dict = matched_row.to_dict(orient="list")
        for key, value in row_dict.items():
            setattr(obj, key, value[0])

    except IndexError:
        c.log(f"\nNo Labjournal Data for {obj.m_id}")


def check_filestart(file: str, string_to_check: str) -> bool:
    """Check if a file starts with a certain string

    Args:
        file (str): file to check
        string_to_check (str): string that is checked if file starts with it

    Returns:
        bool: True if file starts with string_to_check, False if not

    """
    with open(file) as f:
        first_line = f.readline()
    return True if first_line.startswith(string_to_check) else False


def datafile_factory(file: str) -> Optional[DataObject]:
    """Instanciated a data object for the files

    For STM files the stm.stm_factory() function is used

    Args:
        file (str): Full path to the data file from which an object is
            instanciated

    Returns:
        The instanciated data object

    """
    if file.endswith((".mul", ".flm", ".Z_mtrx", ".SM4", ".sxm")):
        return stm_factory(file)
    elif file.endswith(".png"):
        return Image(file)
    elif file.endswith(".txt") and check_filestart(file, "Region"):
        return XpsEis(file)
    elif (
        file.endswith(".dat")
        and check_filestart(file, "Version")
        or file.endswith(".vms")
    ):
        return Aes(file)
    elif file.endswith(".log") and check_filestart(file, "Start Log"):
        return Qcmb(file)
    else:
        return


def instantiate_data_objs(file_lst: List[str]) -> List[DataObject]:
    """Loop to instaciate data object

    Uses the datafile_factory to instaciate data object and adding them to a
    list. StmMul and XpsEis can contain multiple images or spectra,
    respectively. For each of those a object is instaciated and added to the
    list.

    Args:
        file_lst (List[str]): List with full paths to data files

    Returns:
        List of data objects for each STM-Image, Spectrum, etc.

    """
    data_objs: List[DataObject] = []
    for file in track(file_lst, description="> Importing Files  "):
        obj = datafile_factory(file)
        if obj is None:
            continue
        if type(obj) is StmMul:
            data_objs.extend(obj)
        elif type(obj) is XpsEis:
            assert obj.data is not None
            data_objs.extend(obj.data)
        else:
            data_objs.append(obj)

    return [x for x in data_objs if x is not None]


def data_processing(data_objs: List[DataObject], labj: Optional[pd.DataFrame]) -> List[DataObject]:
    """Loop to process DataObjects

    Args:
        data_objs (List[DataObject]): DataObjects for processing
        labj (pandas.DataFrame): Full path to the excel labjournal spreadsheet

    Returns:
        List[DataObject]: The processed DataObjects

    """
    slide_num = 1  # for js modal image slide show in html
    for obj in track(data_objs, description="> Processing"):
        if config.use_labjournal and labj is not None:
            extract_labj(labj, obj)

        if isinstance(obj, MulImage):
            pc.log(f"Processing of [bold cyan]{obj.m_id}[/bold cyan]")
            obj.slide_num = slide_num
            slide_num += 1
            obj.img_data.corr_plane()
            obj.img_data.corr_lines()
            obj.img_data.plot(save=config.save_stm_pngs, save_dir=obj.png_save_dir, save_name=obj.m_id)

        elif isinstance(obj, StmFlm):
            pc.log(f"Processing of [bold cyan]{obj.basename}[/bold cyan]")
            for frame in obj:
                frame.img_data.corr_plane()
                frame.img_data.corr_lines()
            obj.convert_to_mp4()

        elif isinstance(obj, (StmMatrix, StmSm4, StmSxm)):
            pc.log(f"Processing of [bold cyan]{obj.m_id}[/bold cyan]")
            obj.slide_num = slide_num
            slide_num += 1
            obj.img_data_fw.corr_plane()
            obj.img_data_bw.corr_plane()

            obj.img_data_fw.corr_lines()
            obj.img_data_bw.corr_lines()

            obj.img_data_fw.plot(
                save=config.save_stm_pngs, save_dir=obj.png_save_dir, save_name=f"{obj.m_id}_fw"
            )
            obj.img_data_bw.plot(
                save=config.save_stm_pngs, save_dir=obj.png_save_dir, save_name=f"{obj.m_id}_bw"
            )

        elif isinstance(obj, Image):
            pc.log(f"Processing of [bold blue]{obj.m_id}[/bold blue]")
            obj.slide_num = slide_num
            slide_num += 1

        elif isinstance(obj, XpsScan):
            obj.plot()
            pc.log(f"Processing of [bold yellow]{obj.m_id}[/bold yellow]")

        elif isinstance(obj, Aes):
            obj.plot()
            pc.log(f"Processing of [bold yellow]{obj.m_id}[/bold yellow]")

        elif isinstance(obj, Qcmb):
            obj.plot()
            pc.log(f"Processing of [bold pink3]{obj.m_id}[/bold pink3]")

    return data_objs


def main():
    """ """
    # Gui prompt for files
    files_dir = prompt_folder()
    c.log(f"Selected folder:\n{files_dir}")

    # Gui prompt for labjournal
    labj: Optional[pd.DataFrame] = None
    if config.use_labjournal:
        labj_path = prompt_labj()
        if labj_path is not None:
            c.log(f"Selected Labjournal:\n{labj_path}")
            labj = pd.read_excel(labj_path, dtype=str)

    # File import according to mode
    if "day" in config.mode or "daily" in config.mode:
        imported_files, day = import_files_day_mode(files_dir, c)
    else:
        imported_files = import_files_folder_mode(files_dir, c)

    # Object instantiation from files and sorting
    data_objs = sorted(
        instantiate_data_objs(imported_files),
        key=lambda x: x.datetime,
    )

    # Data processing
    data_objs = data_processing(data_objs, labj)

    # Output path of the HTML report according to mode
    if "day" in config.mode or "daily" in config.mode:
        assert day
        output_path = os.path.join(config.path_report_out, str(day.date()))
    else:
        output_path = files_dir

    # HTML report creation and saving
    create_html(data_objs, output_path)
    c.log(
        "[bold green]\u2713[/bold green] HTML-Report created at"
        f" {output_path}_report"
    )


if __name__ == "__main__":
    main()