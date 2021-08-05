import config
import tkinter
import tkinter.filedialog

def prompt_folder():
    root = tkinter.Tk()
    root.withdraw()
    folder = tkinter.filedialog.askdirectory(initialdir=config.path_data)
     
    root.destroy()
    return folder


def prompt_labj():
    root = tkinter.Tk()
    root.withdraw()
    labj_path = tkinter.filedialog.askopenfilename(initialdir=config.path_labjournal,
                                                   filetypes=[("Excel files", '*.xlsx')])
     
    root.destroy()
    return labj_path
