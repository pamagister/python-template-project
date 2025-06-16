import os
import tkinter as tk
from tkinter import filedialog, messagebox

from python_template_project.config.config import ConfigParameterManager
from python_template_project.core.base import PythonProject


class MboxConverterGui:
    def __init__(self, root):
        self.root = root
        self.root.title("Mbox Converter")

        self.mbox_path = tk.StringVar()
        self.format = tk.StringVar(value="txt")
        self.include_from = tk.BooleanVar(value=True)
        self.include_to = tk.BooleanVar(value=True)
        self.include_date = tk.BooleanVar(value=True)
        self.include_subject = tk.BooleanVar(value=True)
        self.max_days = tk.StringVar(value="")

        self._build_widgets()

    def _build_widgets(self):
        frame = tk.Frame(self.root, padx=10, pady=10)
        frame.pack()

        # MBOX selection
        tk.Label(frame, text="MBOX File:").grid(row=0, column=0, sticky="w")
        tk.Entry(frame, textvariable=self.mbox_path, width=40).grid(row=0, column=1)
        tk.Button(frame, text="Browse...", command=self.select_file).grid(row=0, column=2)

        # Format dropdown
        tk.Label(frame, text="Output Format:").grid(row=1, column=0, sticky="w")
        tk.OptionMenu(frame, self.format, "txt", "csv").grid(row=1, column=1, sticky="w")

        # Checkboxes
        tk.Checkbutton(frame, text="Include From", variable=self.include_from).grid(
            row=2, column=0, sticky="w"
        )
        tk.Checkbutton(frame, text="Include To", variable=self.include_to).grid(
            row=3, column=0, sticky="w"
        )
        tk.Checkbutton(frame, text="Include Date", variable=self.include_date).grid(
            row=4, column=0, sticky="w"
        )
        tk.Checkbutton(frame, text="Include Subject", variable=self.include_subject).grid(
            row=5, column=0, sticky="w"
        )

        # Max Days
        tk.Label(frame, text="Max Days per File:").grid(row=6, column=0, sticky="w")
        tk.Entry(frame, textvariable=self.max_days, width=40).grid(row=6, column=1, sticky="w")
        tk.Label(frame, text="blank = unlimited").grid(row=6, column=2, sticky="w")

        # Run Button
        tk.Button(
            frame,
            text="Run Converter",
            command=self.run_parser,
            bg="#4CAF50",
            fg="white",
        ).grid(row=9, column=1, columnspan=1, pady=10)

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("input files", "*.*")])
        if file_path:
            self.mbox_path.set(file_path)

    def run_parser(self):
        path = self.mbox_path.get()
        if not os.path.isfile(path):
            messagebox.showerror("Error", "Please select a valid file.")
            return

        config = ConfigParameterManager("config.yaml")
        parser = PythonProject(config)

        try:
            parser.convert()
            messagebox.showinfo("Done", "Parsing completed successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))


def main():
    """Main entry point for the CLI application."""
    root = tk.Tk()
    MboxConverterGui(root)
    root.mainloop()


if __name__ == "__main__":
    import sys

    sys.exit(main())
