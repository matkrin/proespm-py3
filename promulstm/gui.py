import sys
import tkinter
import tkinter.filedialog
import config


def retry_prompt(prompt_item, retry_fnc):
    """prompt to retry a selection"""

    prompt_retry = input(f"No {prompt_item} selected. Retry? [Y/n]: ")
    if prompt_retry in ['Y', 'y', 'ye', 'yes', 'Ye', 'Yes', '']:
        retry_fnc()
    sys.exit("Exit Programm")


def prompt_folder():
    """prompt to select a folder for data processing"""

    root = tkinter.Tk()
    root.withdraw()
    folder = tkinter.filedialog.askdirectory(initialdir=config.path_data)
    root.destroy()
    if folder == ():
        retry_prompt('folder', prompt_folder)

    return folder


def prompt_labj():
    """prompt to select a labjournal"""

    root = tkinter.Tk()
    root.withdraw()
    labj_path = tkinter.filedialog.askopenfilename(
        initialdir=config.path_labjournal,
        filetypes=[("Excel files", '*.xlsx')]
    )
    root.destroy()
    if labj_path == ():
        retry_prompt("Labjournal", prompt_labj)

    return labj_path
