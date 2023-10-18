from typing import Annotated, List, Union, Optional, cast

from numpy.compat import Path
import os
from rich.console import Console
from rich.progress import track, Progress

# from rich import print
import typer
from mulfile.mul import MulImage


from .config import config
from .stm import (
    stm_factory,
    StmFlm,
    StmMatrix,
    StmMul,
    StmSm4,
    StmSxm,
    NanosurfNid,
    StmType,
)
from .image import Image
from .xps import XpsEis, XpsScan
from .aes import Aes
from .qcmb import Qcmb
from .ec.ec4 import Ec4
from .ec.ec_labview import CaLabview, CvLabview, FftLabview
from .file_import import import_files_day_mode, import_files_folder_mode
from .prompts import prompt_folder, prompt_labj
from .html_rendering import create_html
from .labjournal import LabJournal, LabJournalHeader

app = typer.Typer()

DataObject = Union[
    StmType,
    Image,
    XpsScan,
    Aes,
    Qcmb,
    Ec4,
    CvLabview,
    CaLabview,
    FftLabview,
]

ImportObject = Union[
    DataObject,
    StmMul,
    XpsEis,
]

ExportObject = Union[
    DataObject,
    LabJournalHeader,
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


def check_file_for_str(file: str, string_to_check: str, line_num: int) -> bool:
    """Check if a file starts with a certain string

    Args:
        file (str): file to check
        string_to_check (str): string that is checked if file contains it
        line_num (int): line number which is checked

    Returns:
        bool: True if file starts with string_to_check, False if not

    """
    with open(file) as f:
        [next(f) for _ in range(line_num - 1)]
        line = f.readline()
    return string_to_check in line


def datafile_factory(file: str) -> Optional[ImportObject]:
    """Instanciated a data object for the files

    For STM files the stm.stm_factory() function is used

    Args:
        file (str): Full path to the data file from which an object is
            instanciated

    Returns:
        The instanciated data object

    """
    if file.endswith((".mul", ".flm", ".Z_mtrx", ".SM4", ".sxm", ".nid")):
        return stm_factory(file)
    elif file.endswith((".png", ".jpg", ".jpeg")):
        return Image(file)
    elif file.endswith(".txt") and check_file_for_str(file, "Region", 1):
        return XpsEis(file)
    elif (
        file.endswith(".dat")
        and check_file_for_str(file, "Version", 1)
        or file.endswith(".vms")
    ):
        return Aes(file)
    elif file.endswith(".log") and check_file_for_str(file, "Start Log", 1):
        return Qcmb(file)
    elif file.endswith(".txt") and check_file_for_str(file, "EC4 File", 1):
        return Ec4(file)
    elif (
        file.endswith(".csv")
        and not check_file_for_str(file, "Scan rate", 1)
        and not check_file_for_str(file, "Freq_Hz", 1)
    ):
        return CaLabview(file)
    elif file.endswith(".csv") and check_file_for_str(file, "Scan rate ", 1):
        return CvLabview(file)
    elif file.endswith(".csv") and check_file_for_str(file, "Freq_Hz", 1):
        return FftLabview(file)
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
            data_objs.append(cast(DataObject, obj))

    return [x for x in data_objs if x is not None]


def data_processing(
    data_objs: List[DataObject], labj: Optional[LabJournal]
) -> List[DataObject]:
    """Loop to process DataObjects

    Args:
        data_objs (List[DataObject]): DataObjects for processing
        labj (pandas.DataFrame): Full path to the excel labjournal spreadsheet

    Returns:
        List[DataObject]: The processed DataObjects

    """
    slide_num = 1  # for js modal image slide show in html
    last_ec4: Optional[Ec4] = None
    for obj in track(data_objs, description="> Processing"):
        if labj is not None:
            labj.extract_entry(obj)

        if type(obj) == MulImage:
            pc.log(f"Processing of [bold cyan]{obj.m_id}[/bold cyan]")
            obj.slide_num = slide_num
            slide_num += 1
            obj.img_data.corr_plane()
            obj.img_data.corr_lines()
            obj.img_data.plot(
                save=config.save_stm_pngs,
                save_dir=obj.png_save_dir,
                save_name=obj.m_id,
            )

        elif isinstance(obj, StmFlm):
            pc.log(f"Processing of [bold cyan]{obj.basename}[/bold cyan]")
            for frame in obj:
                frame.img_data.corr_plane()
                frame.img_data.corr_lines()
            obj.convert_to_mp4()

        elif isinstance(obj, (StmMatrix, StmSm4, StmSxm, NanosurfNid)):
            pc.log(f"Processing of [bold cyan]{obj.m_id}[/bold cyan]")
            obj.slide_num = slide_num
            slide_num += 1
            obj.img_data_fw.corr_plane()
            obj.img_data_bw.corr_plane()

            obj.img_data_fw.corr_lines()
            obj.img_data_bw.corr_lines()

            obj.img_data_fw.plot(
                save=config.save_stm_pngs,
                save_dir=obj.png_save_dir,
                save_name=f"{obj.m_id}_fw",
            )
            obj.img_data_bw.plot(
                save=config.save_stm_pngs,
                save_dir=obj.png_save_dir,
                save_name=f"{obj.m_id}_bw",
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
            pc.log(f"Processing of [bold white]{obj.m_id}[/bold white]")

        elif isinstance(obj, Ec4):
            pc.log(f"Processing of [bold pink3]{obj.m_id}[/bold pink3]")
            if obj.filename.endswith("1"):
                last_ec4 = obj
            else:
                assert last_ec4 is not None
                last_ec4.push_cv_data(obj)

            last_ec4.plot()

        elif isinstance(obj, (CvLabview, CaLabview, FftLabview)):
            pc.log(f"Processing of [bold pink3]{obj.m_id}[/bold pink3]")
            obj.plot()

    return [
        x
        for x in data_objs
        if not (isinstance(x, Ec4) and not x.filename.endswith("1"))
    ]


def main_loop_folder_mode(
    import_files_dir: str,
    output_dir: str,
    use_labjournal: bool,
    labjournal_path: str | None = None,
):
    c = Console()
    labj: Optional[LabJournal] = None

    # Gui prompt for labjournal
    if use_labjournal and labjournal_path is not None:
        labj = LabJournal(labjournal_path)
        c.log(f"Selected Labjournal:\n{labjournal_path}")

    imported_files = import_files_folder_mode(import_files_dir, c)

    # Object instantiation from files and sorting
    data_objs = sorted(
        instantiate_data_objs(imported_files),
        key=lambda x: x.datetime,
    )

    # Data processing
    data_objs = cast(list[ExportObject], data_processing(data_objs, labj))
    if use_labjournal and labj is not None:
        data_objs.extend(labj.read_header())
        labj.close()

    # HTML report creation and saving
    output_name = os.path.basename(import_files_dir)
    output_path = os.path.join(output_dir, output_name)
    create_html(data_objs, output_path, output_name)
    c.log(
        "[bold green]\u2713[/bold green] HTML-Report created at"
        f" {output_path}_report"
    )


def main_loop_day_mode(
    import_files_dir: str,
    output_dir: str,
    use_labjournal: bool,
    labjournal_path: str | None = None,
):
    imported_files, day = import_files_day_mode(import_files_dir, c)

    # Object instantiation from files and sorting
    data_objs = sorted(
        instantiate_data_objs(imported_files),
        key=lambda x: x.datetime,
    )

    # Data processing
    labj: LabJournal | None = None
    if use_labjournal and labjournal_path is not None:
        labj = LabJournal(labjournal_path)
    data_objs = cast(list[ExportObject], data_processing(data_objs, labj))
    if use_labjournal and labj is not None:
        data_objs.extend(labj.read_header())
        labj.close()

    output_path = os.path.join(output_dir, str(day.date()))
    output_name = os.path.basename(output_path)
    create_html(data_objs, output_path, output_name)
    c.log(
        "[bold green]\u2713[/bold green] HTML-Report created at"
        f" {output_path}_report"
    )


def main():
    """ """
    # Gui prompt for files
    files_dir = prompt_folder()
    c.log(f"Selected folder:\n{files_dir}")

    # Gui prompt for labjournal
    labj_path: str | None = None
    if config.use_labjournal:
        labj_path = prompt_labj()

    # File import according to mode
    if "day" in config.mode or "daily" in config.mode:
        main_loop_day_mode(
            files_dir, config.path_report_out, config.use_labjournal, labj_path
        )
    else:
        main_loop_folder_mode(
            files_dir, files_dir, config.use_labjournal, labj_path
        )


@app.command()
def cli(testing: Annotated[bool, typer.Option("--test", "-t")] = False):
    if not testing:
        main()
    else:
        files_dir = Path(__file__).parent.parent / "tests" / "test_files"
        labj_path = (
            Path(__file__).parent.parent
            / "tests"
            / "test_files"
            / "1_lab_journal_new.xlsx"
        )
        main_loop_folder_mode(
            str(files_dir), str(files_dir), True, str(labj_path)
        )


if __name__ == "__main__":
    main()
