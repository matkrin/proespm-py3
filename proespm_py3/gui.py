import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog
import pathlib
import sys

from .proespm_py3 import main_loop_folder_mode_data_driven


ENTRY_WIDTH = 75


class App:
    """Class handeling the gui"""

    def __init__(self) -> None:
        self.root = tk.Tk()

        self.data_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.labj = tk.StringVar()

        self.use_labj_checked = tk.BooleanVar()
        self.is_disabled = tk.StringVar(value="disabled")

        self.frame_data = ttk.LabelFrame(self.root, text="Data")
        # Data
        self.lbl_data = ttk.Label(master=self.frame_data, text="Data Path: ")
        self.ent_data = ttk.Entry(
            master=self.frame_data,
            width=ENTRY_WIDTH,
            # state="readonly",
            textvariable=self.data_dir,
        )
        self.btn_data = ttk.Button(
            master=self.frame_data, text="Browse", command=self.prompt_data_dir
        )
        # Output
        self.lbl_output = ttk.Label(
            master=self.frame_data, text="Output Path: "
        )
        self.ent_output = ttk.Entry(
            master=self.frame_data,
            width=ENTRY_WIDTH,
            textvariable=self.output_dir,
        )
        self.btn_output = ttk.Button(
            master=self.frame_data,
            text="Browse",
            command=self.prompt_output_dir,
        )
        # Spreadsheet
        self.frame_labj = ttk.LabelFrame(self.root, text="Spreadsheet")
        self.lbl_labj = ttk.Label(
            master=self.frame_labj,
            text="Spreadsheet: ",
            state=self.is_disabled.get(),
        )
        self.ent_labj = ttk.Entry(
            master=self.frame_labj,
            width=ENTRY_WIDTH,
            state=self.is_disabled.get(),
            textvariable=self.labj,
        )
        self.btn_labj = ttk.Button(
            master=self.frame_labj,
            text="Browse",
            state=self.is_disabled.get(),
            command=self.prompt_labj,
        )
        self.check_use_labj = ttk.Checkbutton(
            master=self.frame_labj,
            text="Use Spreadsheet?",
            variable=self.use_labj_checked,
            command=self.toggle_labj,
        )
        # Run controls
        self.run_frame = ttk.Frame(self.root)
        self.run_btn = ttk.Button(
            master=self.run_frame,
            text="Run",
            default="active",
            command=self.run_processing,
        )
        self.quit_btn = ttk.Button(
            master=self.run_frame, text="Quit", command=self.quit
        )

        self.create_layout()

    def run(self):
        self.root.mainloop()

    def quit(self):
        self.root.destroy()
        sys.exit(0)

    def create_layout(self):
        opts = {"padx": 5, "pady": 5, "sticky": "w"}
        self.frame_data.grid(column=0, row=0, **opts)
        self.lbl_data.grid(column=0, row=0, **opts)
        self.ent_data.grid(column=1, row=0, **opts)
        self.btn_data.grid(column=2, row=0, **opts)
        self.lbl_output.grid(column=0, row=1, **opts)
        self.ent_output.grid(column=1, row=1, **opts)
        self.btn_output.grid(column=2, row=1, **opts)

        self.frame_labj.grid(column=0, row=1, **opts)
        self.lbl_labj.grid(column=0, row=1, **opts)
        self.ent_labj.grid(column=1, row=1, **opts)
        self.btn_labj.grid(column=2, row=1, **opts)
        self.check_use_labj.grid(column=0, row=0, columnspan=2, **opts)

        self.run_frame.grid(column=0, row=2)
        self.run_btn.grid(column=0, row=0, padx="5", pady="5")
        self.quit_btn.grid(column=1, row=0, padx="5", pady="5")

    def toggle_labj(self):
        state = "normal" if self.use_labj_checked.get() else "disabled"
        self.is_disabled.set(state)
        self.ent_labj.configure(state=state)
        self.btn_labj.configure(state=state)
        self.lbl_labj.configure(state=state)

    def prompt_data_dir(self):
        dir = tkinter.filedialog.askdirectory()
        parent = pathlib.Path(dir).parent
        self.data_dir.set(dir)
        self.output_dir.set(str(parent))

    def prompt_output_dir(self):
        dir = tkinter.filedialog.askdirectory()
        self.output_dir.set(dir)

    def prompt_labj(self):
        labj = tkinter.filedialog.askopenfilename(
            # initialdir=config.path_labjournal,
            filetypes=[("Excel files", "*.xlsx")],
        )
        self.labj.set(labj)

    def run_processing(self):
        import_files_dir = self.data_dir.get()
        output_dir = self.output_dir.get()
        labjournal_path = self.labj.get()
        use_labjournal = self.use_labj_checked.get()
        main_loop_folder_mode_data_driven(
            import_files_dir, output_dir, use_labjournal, labjournal_path
        )
