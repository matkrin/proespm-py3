import os
import pandas as pd
from rich import print
from rich.console import Console
from rich.progress import track, Progress
import config
from stm_mul import Mul, StmMul
from stm_matrix import StmMatrix
from image import Image
from xps import XpsVtStm, XpsScan
from xps_hippie import XpsHippie
from gui import prompt_folder, prompt_labj
from html_rendering import create_html


c = Console()   # normal logging
pc = Progress().console     # logging in loops with track()

allowed_ftypes = ('.mul', '.png', '.txt', '.Z_mtrx')



def extract_labj(labjournal, obj):
    """
    """
    try:
        matched_row = labjournal[labjournal['ID'].str.match(obj.m_id)]
        row_dict = matched_row.to_dict(orient='list')
        for key, value in row_dict.items():
            setattr(obj, key, value[0])

    except IndexError:
        c.log(f"\nNo Labjournal Data for {obj.m_id}")


def check_filestart(file, string_to_check):
    """
    Check if a file starts with a certain string

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
    labj_dir = prompt_labj()
    c.log(f"Selected Labjournal:\n{labj_dir}")
    labj = pd.read_excel(labj_dir, dtype=str)


# get filepaths for prompted folder
file_lst = []   # full paths
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
    if file.endswith('.mul'):
        mul = Mul(file)
        mul_stm_imgs = [StmMul(img_dic) for img_dic in mul.img_lst]
        cls_objs += mul_stm_imgs
    elif file.endswith('.Z_mtrx'):
        obj = StmMatrix(file)
        cls_objs.append(obj)
    elif file.endswith('.png'):
        obj = Image(file)
        cls_objs.append(obj)
    elif file.endswith('.txt') and check_filestart(file, 'Region'):
        xps_vt = XpsVtStm(file)
        xps_vt_scans = [XpsScan(scan_dict, file) for scan_dict in xps_vt.data]
        cls_objs += xps_vt_scans
    elif file.endswith('.txt') and check_filestart(file, '[Info]'):
        xps_hippie = XpsHippie(file)
        xps_hippie_scans = [XpsScan(scan_dict, file) for scan_dict in xps_hippie.data]
        cls_objs += xps_hippie_scans


#sort by datetime
cls_objs = sorted(cls_objs, key=lambda x: str(x.datetime))

slide_num = 1 # for modal image slide show in html
for obj in track(cls_objs, description="> Processing"):
    if config.use_labjournal:
        extract_labj(labj, obj)

    if type(obj).__name__ == 'StmMul':
        pc.log(f"Processing of [bold cyan]{obj.m_id}[/bold cyan]")
        obj.slide_num = slide_num
        slide_num += 1
        obj.corr_plane(obj.img_data)
        obj.corr_lines(obj.img_data)
        obj.plot(save=True, show=False)
        obj.add_png()

    if type(obj).__name__ == 'StmMatrix':
        pc.log(f"Processing of [bold cyan]{obj.m_id}[/bold cyan]")
        obj.slide_num = slide_num
        slide_num += 1
        obj.corr_plane(obj.img_data_fw)
        obj.corr_plane(obj.img_data_bw)
        obj.corr_lines(obj.img_data_fw)
        obj.corr_lines(obj.img_data_bw)
        obj.plot_fw(save=True, show=False)
        obj.plot_bw(save=True, show=False)
        obj.add_png()

    if type(obj).__name__ == 'Image':
        pc.log(f"Processing of [bold blue]{obj.m_id}[/bold blue]")
        obj.slide_num = slide_num
        slide_num += 1

    if type(obj).__name__ == 'XpsScan':
        pc.log(f"Processing of [bold yellow]{obj.m_id}[/bold yellow]")
        if obj.xps == 'maxlab_hippie':
            obj.save_plain_data(files_dir)
            pc.log(f"Saved plain data as txt of {obj.m_id}")


create_html(cls_objs, files_dir)
c.log("HTML-Report created " +  u"[bold green]\u2713[/bold green]")
