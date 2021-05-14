import os
import pandas as pd
from rich import print
from rich.console import Console
from rich.progress import track, Progress
from mul import Mul
from stm import Stm
from image import Image
from gui import prompt_folder, prompt_labj
from html import create_html

c = Console()
pc = Progress().console

allowed_ftypes = (".mul", ".png")

def extract_labj(labjournal, obj):
    matched_row = labj[labj['ID'].str.match(obj.img_id)]
    row_dict = matched_row.to_dict(orient='list')
    for key in row_dict:
        setattr(obj, key, row_dict[key][0])

# gui prompt
files_dir = prompt_folder()
labj_dir = prompt_labj()
c.log(f"Selected folder:\n{files_dir}")
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
    if file.endswith(".mul"):
        mul = Mul(file)
        stm_imgs = [Stm(img_dic) for img_dic in mul.img_lst]
        cls_objs += stm_imgs
    elif file.endswith(".png"):
        obj = Image(file)
        cls_objs.append(obj)

#sort by datetime
cls_objs = sorted(cls_objs, key=lambda x: str(x.datetime))

slide_num = 1 # for modal image slide show
for obj in track(cls_objs, description="> Processing Images"):

    #matched_row = labj[labj['ID'].str.match(obj.img_id)]
    #row_dict = matched_row.to_dict(orient='list')
    #for key in row_dict:
    #    setattr(obj, key, row_dict[key][0])
    extract_labj(labj, obj)

    if type(obj).__name__ == 'Image':
        pc.log(f"Processing of [bold blue]{obj.filename}[/bold blue]")
        obj.slide_num = slide_num
        slide_num += 1

    if type(obj).__name__ == 'Stm':
        pc.log(f"Processing of [bold cyan]{obj.img_id}[/bold cyan]")
        obj.slide_num = slide_num
        slide_num += 1
        obj.corr_plane()
        obj.corr_lines()
        obj.plot(files_dir, save=True)
        obj.add_png(files_dir)

create_html(cls_objs, files_dir)
c.log("HTML-Report created " +  u"[bold green]\u2713[/bold green]")
