import os
import pandas as pd
from rich import print
from rich.console import Console
from rich.progress import track, Progress
from mulfile.mul import MulImage
import config
from stm_mul import StmMul
from stm_flm import Flm
from stm_matrix import StmMatrix
from stm_sm4 import StmSm4
from stm_sxm import StmSxm
from image import Image
from xps import XpsVtStm, XpsScan
from aes import Aes
from qcmb import Qcmb
from gui import prompt_folder, prompt_labj
from html_rendering import create_html


c = Console()  # normal logging
pc = Progress().console  # logging in loops with track()

allowed_ftypes = (
    ".mul",
    ".png",
    ".txt",
    ".Z_mtrx",
    ".flm",
    ".log",
    ".SM4",
    ".dat",
    ".sxm",
)


def extract_labj(labjournal, obj):
    """extract data of a labjournal excel file"""

    try:
        matched_row = labjournal[labjournal["ID"].str.match(obj.m_id)]
        row_dict = matched_row.to_dict(orient="list")
        for key, value in row_dict.items():
            setattr(obj, key, value[0])

    except IndexError:
        c.log(f"\nNo Labjournal Data for {obj.m_id}")


def check_filestart(file, string_to_check):
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


# gui prompt for files
files_dir = prompt_folder()
c.log(f"Selected folder:\n{files_dir}")

# gui prompt for labjournal
if config.use_labjournal:
    labj_path = prompt_labj()
    if labj_path is not None:
        c.log(f"Selected Labjournal:\n{labj_path}")
        labj = pd.read_excel(labj_path, dtype=str)

# get filepaths for prompted folder
file_lst = []  # full paths
for entry in os.scandir(files_dir):
    if entry.path.endswith(allowed_ftypes) and entry.is_file():
        file_lst.append(entry.path)
        c.log(f"Detected File:\t\t[green]{os.path.basename(entry.path)}[/green]")
    elif not entry.path.endswith(allowed_ftypes) and entry.is_file():
        c.log(f"Unsupported File:\t[red]{os.path.basename(entry.path)}[/red]")
    elif not entry.is_file():
        c.log(f"Ignored Folder:\t\t[red]{os.path.basename(entry.path)}[/red]")

# create class instances
cls_objs = []
for file in track(file_lst, description="> Importing Files  "):
    if file.endswith(".mul"):
        mul = StmMul(file)
        # mul_stm_imgs = [StmMul(img_dic) for img_dic in mul.img_lst]
        # cls_objs += mul_stm_imgs
        for image in mul:
            cls_objs.append(image)
    elif file.endswith(".flm"):
        flm = Flm(file)
        cls_objs.append(flm)
    elif file.endswith(".Z_mtrx"):
        stm_matrix = StmMatrix(file)
        cls_objs.append(stm_matrix)
    elif file.endswith(".SM4"):
        stm_sm4 = StmSm4(file)
        cls_objs.append(stm_sm4)
    elif file.endswith(".sxm"):
        stm_sxm = StmSxm(file)
        cls_objs.append(stm_sxm)
    elif file.endswith(".png"):
        image = Image(file)
        cls_objs.append(image)
    elif file.endswith(".txt") and check_filestart(file, "Region"):
        xps_vt = XpsVtStm(file)
        xps_vt_scans = [XpsScan(scan_dict, file) for scan_dict in xps_vt.data]
        cls_objs += xps_vt_scans
    elif file.endswith(".dat") and check_filestart(file, "Version"):
        aes = Aes(file)
        cls_objs.append(aes)
    elif file.endswith(".log") and check_filestart(file, "Start Log"):
        qcmb = Qcmb(file)
        cls_objs.append(qcmb)

# sort by datetime
cls_objs = sorted(cls_objs, key=lambda x: str(x.datetime))

slide_num = 1  # for js modal image slide show in html
for obj in track(cls_objs, description="> Processing"):
    if config.use_labjournal and labj_path is not None:
        extract_labj(labj, obj)

    if isinstance(obj, MulImage):
        pc.log(f"Processing of [bold cyan]{obj.m_id}[/bold cyan]")
        obj.slide_num = slide_num
        slide_num += 1
        obj.img_data.corr_plane()
        obj.img_data.corr_lines()
        obj.img_data.plot()

    elif isinstance(obj, Flm):
        pc.log(f"Processing of [bold cyan]{obj.basename}[/bold cyan]")
        # for frame in obj:
        #     frame.corr_plane()
        #     frame.corr_lines()
        obj.convert_to_mp4()

    elif isinstance(obj, (StmMatrix, StmSm4, StmSxm)):
        pc.log(f"Processing of [bold cyan]{obj.m_id}[/bold cyan]")
        obj.slide_num = slide_num
        slide_num += 1
        obj.img_data_fw.corr_plane()
        obj.img_data_bw.corr_plane()

        obj.img_data_fw.corr_lines()
        obj.img_data_bw.corr_lines()

        obj.img_data_fw.plot()
        obj.img_data_bw.plot()

    elif isinstance(obj, Image):
        pc.log(f"Processing of [bold blue]{obj.m_id}[/bold blue]")
        obj.slide_num = slide_num
        slide_num += 1

    elif isinstance(obj, XpsScan):
        pc.log(f"Processing of [bold yellow]{obj.m_id}[/bold yellow]")

    elif isinstance(obj, Aes):
        pc.log(f"Processing of [bold yellow]{obj.m_id}[/bold yellow]")

    elif isinstance(obj, Qcmb):
        pc.log(f"Processing of [bold pink3]{obj.m_id}[/bold pink3]")

create_html(cls_objs, files_dir)
c.log("HTML-Report created " + "[bold green]\u2713[/bold green]")
