import tkinter as tk
from tkinter import messagebox, ttk

from python_template_project.config.config import ConfigParameter, ConfigParameterManager
from python_template_project.core.logging import get_logger


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
