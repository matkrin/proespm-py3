import sys
import tkinter
import tkinter.filedialog
import config


def prompt_folder():
    """prompt to select a folder for data processing"""

    root = tkinter.Tk()
    root.withdraw()
    folder = tkinter.filedialog.askdirectory(initialdir=config.path_data)
    if folder == () or folder == "" or folder == None:
        prompt_retry = input("No data folder selected. Retry? [Y/n] ")
        if prompt_retry in ["Y", "y", "ye", "yes", "Ye", "Yes", ""]:
            return prompt_folder()
        else:
            sys.exit("Exit Programm")

    return folder


def prompt_labj():
    """prompt to select a labjournal"""

    root = tkinter.Tk()
    root.withdraw()
    labj_path = tkinter.filedialog.askopenfilename(
        initialdir=config.path_labjournal,
        filetypes=[("Excel files", "*.xlsx")],
    )
    if labj_path == () or labj_path == "" or labj_path == None:
        prompt_continue = input(
            "No Labjournal selected. Continue without? [Y/n] "
        )
        if prompt_continue in ["Y", "y", "ye", "yes", "Ye", "Yes", ""]:
            labj_path = None
            return labj_path
        else:
            return prompt_labj()
    else:
        return labj_path
