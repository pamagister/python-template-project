"""GUI interface for python-template-project using tkinter with integrated logging.

This module provides a graphical user interface for the python-template-project
with settings dialog, file management, and centralized logging capabilities.

run gui: python -m python_template_project.gui
"""

import os
import sys
import threading
import tkinter as tk
import traceback
import webbrowser
from functools import partial
from tkinter import filedialog, messagebox, ttk

from python_template_project.config.config import ConfigParameter, ConfigParameterManager
from python_template_project.core.base import BaseGPXProcessor
from python_template_project.core.logging import (
    connect_gui_logging,
    disconnect_gui_logging,
    get_logger,
    initialize_logging,
)


class ToolTip:
    """Create a tooltip for a given widget."""

    def __init__(self, widget, text="widget info"):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)

    def on_enter(self, event=None):
        self.show_tooltip()

    def on_leave(self, event=None):
        self.hide_tooltip()

    def show_tooltip(self):
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + cy + self.widget.winfo_rooty() + 25
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw,
            text=self.text,
            justify=tk.LEFT,
            background="#ffffe0",
            relief=tk.SOLID,
            borderwidth=1,
            font=("tahoma", "8", "normal"),
        )
        label.pack(ipadx=1)

    def hide_tooltip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


class GuiLogWriter:
    """Log writer that handles GUI text widget updates in a thread-safe way."""

    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.root = text_widget.winfo_toplevel()

    def write(self, text):
        """Write text to the widget in a thread-safe manner."""
        # Schedule the GUI update in the main thread
        self.root.after(0, self._update_text, text)

    def _update_text(self, text):
        """Update the text widget (must be called from main thread)."""
        try:
            self.text_widget.insert(tk.END, text)
            self.text_widget.see(tk.END)
            self.text_widget.update_idletasks()
        except tk.TclError:
            # Widget might be destroyed
            pass

    def flush(self):
        """Flush method for compatibility."""
        pass


class SettingsDialog:
    """Settings dialog for configuration management."""

    def __init__(self, parent, config_manager: ConfigParameterManager):
        self.parent = parent
        self.config_manager = config_manager
        self.result = None
        self.widgets = {}
        self.logger = get_logger("gui.settings")

        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Settings")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center the dialog
        self.dialog.geometry(f"+{int(parent.winfo_rootx() + 50)}+{int(parent.winfo_rooty() + 50)}")

        self._create_widgets()

        # Handle window closing
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)

        self.logger.debug("Settings dialog opened")

    def _create_widgets(self):
        """Create the settings dialog widgets."""
        # Main frame
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create tabs for each configuration category
        self._create_cli_tab()
        self._create_app_tab()
        self._create_gui_tab()

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(button_frame, text="OK", command=self._on_ok).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self._on_cancel).pack(side=tk.RIGHT)

    def _create_cli_tab(self):
        """Create CLI configuration tab."""
        cli_frame = ttk.Frame(self.notebook)
        self.notebook.add(cli_frame, text="CLI")

        # Create scrollable frame
        canvas = tk.Canvas(cli_frame)
        scrollbar = ttk.Scrollbar(cli_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Add parameters
        self._add_category_parameters(scrollable_frame, "cli", self.config_manager.cli)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _create_app_tab(self):
        """Create App configuration tab."""
        app_frame = ttk.Frame(self.notebook)
        self.notebook.add(app_frame, text="App")

        # Create scrollable frame
        canvas = tk.Canvas(app_frame)
        scrollbar = ttk.Scrollbar(app_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Add parameters
        self._add_category_parameters(scrollable_frame, "app", self.config_manager.app)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _create_gui_tab(self):
        """Create GUI configuration tab."""
        gui_frame = ttk.Frame(self.notebook)
        self.notebook.add(gui_frame, text="GUI")

        # Create scrollable frame
        canvas = tk.Canvas(gui_frame)
        scrollbar = ttk.Scrollbar(gui_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Add parameters
        self._add_category_parameters(scrollable_frame, "gui", self.config_manager.gui)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _add_category_parameters(self, parent, category_name, category_obj):
        """Add parameter widgets for a specific category."""
        row = 0
        for field_name in category_obj.model_fields:
            param = getattr(category_obj, field_name)
            if param.required:
                # Skip required parameters as they are not configurable in GUI
                # --> required params have to be set via Open file dialog in GUI
                continue

            # Create label
            label = ttk.Label(parent, text=f"{param.name}:")
            label.grid(row=row, column=0, sticky="w", padx=5, pady=2)

            # Create appropriate widget based on parameter type
            widget = self._create_parameter_widget(parent, param)
            widget.grid(row=row, column=1, sticky="ew", padx=5, pady=2)

            # Add tooltip
            ToolTip(label, param.help)
            ToolTip(widget, param.help)

            # Store widget reference
            self.widgets[f"{category_name}__{param.name}"] = widget

            row += 1

        # Configure column weights
        parent.columnconfigure(1, weight=1)

    def _create_parameter_widget(self, parent, param: ConfigParameter):
        """Create appropriate widget for parameter type."""
        if param.type_ == bool:
            # Checkbox for boolean values
            var = tk.BooleanVar(value=param.default)
            widget = ttk.Checkbutton(parent, variable=var)
            widget.var = var
            return widget

        elif param.choices and param.type_ != bool:
            # Combobox for choices
            var = tk.StringVar(value=str(param.default))
            widget = ttk.Combobox(parent, textvariable=var, values=param.choices, state="readonly")
            widget.var = var
            return widget

        elif param.type_ == int:
            # Spinbox for integers
            var = tk.IntVar(value=param.default)
            widget = ttk.Spinbox(parent, from_=-999999, to=999999, textvariable=var)
            widget.var = var
            return widget

        else:  # str or other types
            # Entry for strings
            var = tk.StringVar(value=str(param.default))
            widget = ttk.Entry(parent, textvariable=var)
            widget.var = var
            return widget

    def _on_ok(self):
        """Handle OK button click."""
        try:
            # Update configuration with widget values
            overrides = {}
            for key, widget in self.widgets.items():
                value = widget.var.get()
                overrides[key] = value

            self.logger.info(f"Applying configuration overrides: {len(overrides)} settings")

            # Apply overrides to config manager
            self.config_manager._apply_kwargs(overrides)

            # Save to file
            self.config_manager.save_to_file("config.yaml")
            self.logger.info("Configuration saved successfully")

            self.result = "ok"
            self.dialog.destroy()

        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            messagebox.showerror("Error", f"Failed to save configuration: {e}")

    def _on_cancel(self):
        """Handle Cancel button click."""
        self.logger.debug("Settings dialog cancelled")
        self.result = "cancel"
        self.dialog.destroy()


class MainGui:
    """Main GUI application class."""

    processing_modes = [
        ("compress_files", "Compress"),
        ("merge_files", "Merge"),
        ("extract_pois", "Extract POIs"),
    ]

    def __init__(self, root):
        self.root = root
        self.root.title("python-template-project")
        self.root.geometry("800x600")

        # Initialize configuration
        self.config_manager = ConfigParameterManager()

        # Initialize logging system
        self.logger_manager = initialize_logging(self.config_manager)
        self.logger = get_logger("gui.main")

        # File list
        self.file_list = []

        self._build_widgets()
        self._create_menu()

        # Setup GUI logging after widgets are created
        self._setup_gui_logging()

        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        self.logger.info("GUI application started")
        self.logger_manager.log_config_summary()

    def _build_widgets(self):
        """Build the main GUI widgets."""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Top frame for file list and run button
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.BOTH, expand=True)

        # Left side - File list
        file_frame = ttk.LabelFrame(top_frame, text="Input Files")
        file_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # File listbox with scrollbar
        listbox_frame = ttk.Frame(file_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.file_listbox = tk.Listbox(listbox_frame)
        file_scrollbar = ttk.Scrollbar(
            listbox_frame, orient="vertical", command=self.file_listbox.yview
        )
        self.file_listbox.configure(yscrollcommand=file_scrollbar.set)

        self.file_listbox.pack(side="left", fill="both", expand=True)
        file_scrollbar.pack(side="right", fill="y")

        # Right side - Run button and controls
        button_frame = ttk.Frame(top_frame)
        button_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))

        open_button = ttk.Button(button_frame, text="Open Files", command=self._open_files)
        open_button.pack(pady=8)

        # Create buttons dynamically
        self.run_buttons = {}
        for mode, label in self.processing_modes:
            button = ttk.Button(
                button_frame, text=label, command=partial(self._run_processing, mode=mode)
            )
            button.pack(pady=1)
            # Save buttons in dictionary for later access
            self.run_buttons[mode] = button

        # Clear files button
        self.clear_button = ttk.Button(button_frame, text="Clear Files", command=self._clear_files)
        self.clear_button.pack(pady=8)

        # Progress bar
        self.progress = ttk.Progressbar(button_frame, mode="indeterminate")
        self.progress.pack(pady=5, fill=tk.X)

        # Bottom frame - Log output
        log_frame = ttk.LabelFrame(main_frame, text="Log Output")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        # Log text widget with scrollbar
        log_text_frame = ttk.Frame(log_frame)
        log_text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.log_text = tk.Text(log_text_frame, height=10, wrap=tk.WORD)
        log_text_scrollbar = ttk.Scrollbar(
            log_text_frame, orient="vertical", command=self.log_text.yview
        )
        self.log_text.configure(yscrollcommand=log_text_scrollbar.set)

        self.log_text.pack(side="left", fill="both", expand=True)
        log_text_scrollbar.pack(side="right", fill="y")

        # Log controls
        log_controls = ttk.Frame(log_frame)
        log_controls.pack(fill=tk.X, padx=5, pady=(0, 5))

        ttk.Button(log_controls, text="Clear Log", command=self._clear_log).pack(side=tk.LEFT)

        # Log level selector
        ttk.Label(log_controls, text="Log Level:").pack(side=tk.LEFT, padx=(10, 5))
        self.log_level_var = tk.StringVar(value=self.config_manager.app.log_level.default)
        log_level_combo = ttk.Combobox(
            log_controls,
            textvariable=self.log_level_var,
            values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            state="readonly",
            width=10,
        )
        log_level_combo.pack(side=tk.LEFT)
        log_level_combo.bind("<<ComboboxSelected>>", self._on_log_level_changed)

    def _create_menu(self):
        """Create the application menu."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open...", command=self._open_files)
        file_menu.add_separator()

        # Create Run menu options dynamically
        for mode, label in self.processing_modes:
            file_menu.add_command(label=label, command=partial(self._run_processing, mode=mode))

        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing)

        # Options menu
        options_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Options", menu=options_menu)
        options_menu.add_command(label="Settings", command=self._open_settings)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User help", command=self._open_help)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self._show_about)

    def _setup_gui_logging(self):
        """Setup GUI logging integration."""
        # Create GUI log writer
        self.gui_log_writer = GuiLogWriter(self.log_text)

        # Connect to logging system
        connect_gui_logging(self.gui_log_writer)

    def _on_log_level_changed(self, event=None):
        """Handle log level change."""
        new_level = self.log_level_var.get()
        self.logger_manager.set_log_level(new_level)
        self.logger.info(f"Log level changed to {new_level}")

    def _clear_log(self):
        """Clear the log text widget."""
        self.log_text.delete(1.0, tk.END)
        self.logger.debug("Log display cleared")

    def _clear_files(self):
        """Clear the file list."""
        self.file_list.clear()
        self.file_listbox.delete(0, tk.END)
        self.logger.info("File list cleared")

    def _open_files(self):
        """Open file dialog and add files to list."""
        files = filedialog.askopenfilenames(
            title="Select input files", filetypes=[("All files", "*.*"), ("Text files", "*.txt")]
        )

        new_files = 0
        for file in files:
            if file not in self.file_list:
                self.file_list.append(file)
                self.file_listbox.insert(tk.END, os.path.basename(file))
                new_files += 1

        if new_files > 0:
            self.logger.info(f"Added {new_files} new files to processing list")
        else:
            self.logger.debug("No new files selected")

    def _run_processing(self, mode="compress_files"):
        """Run the processing in a separate thread."""
        if not self.file_list:
            self.logger.warning("No input files selected")
            messagebox.showwarning("Warning", "No input files selected!")
            return

        self.logger.info(f"Starting processing of {len(self.file_list)} files in mode: {mode}")

        # Alle Buttons während der Verarbeitung deaktivieren
        for button in self.run_buttons.values():
            button.config(state="disabled")
        self.progress.start()

        # Run in separate thread to avoid blocking GUI
        thread = threading.Thread(target=self._process_files, args=(mode,), daemon=True)
        thread.start()

    def _process_files(self, mode="compress_files"):
        """Process the selected files."""
        try:
            self.logger.info("=== Processing Started ===")
            self.logger.info("Processing files...")

            # Create and run project
            project = BaseGPXProcessor(
                self.file_list,
                self.config_manager.cli.output.default,
                self.config_manager.cli.min_dist.default,
                self.config_manager.app.date_format.default,
                self.config_manager.cli.elevation.default,
                self.logger,
            )
            # implement switch case for different processing modes
            if mode == "compress_files":
                project.compress_files()
            elif mode == "merge_files":
                project.merge_files()
            elif mode == "extract_pois":
                project.extract_pois()
            else:
                self.logger.warning(f"Unknown mode: {mode}")

            self.logger.info(f"Completed: {len(self.file_list)} files processed")

            self.logger.info("=== All files processed successfully! ===")

        except Exception as err:
            self.logger.error(f"Processing failed: {err}", exc_info=True)
            # Show error dialog in main thread
            self.root.after(
                0, lambda e=err: messagebox.showerror("Error", f"Processing failed: {e}")
            )

        finally:
            # Re-enable controls in main thread
            self.root.after(0, self._processing_finished)

    def _processing_finished(self):
        """Re-enable controls after processing is finished."""
        for button in self.run_buttons.values():
            button.config(state="normal")
        self.clear_button.config(state="normal")
        self.progress.stop()

    def _open_settings(self):
        """Open the settings dialog."""
        self.logger.debug("Opening settings dialog")
        dialog = SettingsDialog(self.root, self.config_manager)
        self.root.wait_window(dialog.dialog)

        if dialog.result == "ok":
            self.logger.info("Settings updated successfully")
            # Update log level selector if it changed
            self.log_level_var.set(self.config_manager.app.log_level.default)

    def _open_help(self):
        """Open help documentation in browser."""
        self.logger.debug("Opening help documentation")
        webbrowser.open("https://python-template-project.readthedocs.io/en/stable/")

    def _show_about(self):
        """Show about dialog."""
        self.logger.debug("Showing about dialog")
        messagebox.showinfo("About", "python-template-project\n\nCopyright by Paul")

    def _on_closing(self):
        """Handle application closing."""
        self.logger.info("Closing GUI application")
        disconnect_gui_logging()
        self.root.quit()
        self.root.destroy()


def main():
    """Main entry point for the GUI application."""
    root = tk.Tk()
    try:
        MainGui(root)
        root.mainloop()
    except Exception as e:
        print(f"GUI startup failed: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
