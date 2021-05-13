import tkinter
import tkinter.filedialog

def prompt_folder():
    root = tkinter.Tk()
    root.withdraw()
    folder = tkinter.filedialog.askdirectory(initialdir='~/projects/promulstm/test')
     
    root.destroy()
    return folder


def prompt_labj():
    root = tkinter.Tk()
    root.withdraw()
    labj_path = tkinter.filedialog.askopenfilename(initialdir='~/projects/promulstm/test',
                                                   filetypes=[("Excel files", '*.xlsx')])
     
    root.destroy()
    return labj_path
