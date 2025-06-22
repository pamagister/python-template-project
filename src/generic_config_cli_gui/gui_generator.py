# config_framework/gui.py
"""Generic GUI settings dialog generator for configuration framework."""

import tkinter as tk
from tkinter import messagebox, ttk

from generic_config_cli_gui.config_framework import ConfigManager, ConfigParameter


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


class SettingsDialogGenerator:
    """Generates settings dialog from ConfigManager."""

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager

    def create_settings_dialog(
        self, parent, title="Settings", config_file="config.yaml"
    ) -> "GenericSettingsDialog":
        """Create a settings dialog for the configuration."""
        return GenericSettingsDialog(parent, self.config_manager, title, config_file)


class GenericSettingsDialog:
    """Generic settings dialog for ConfigManager."""

    def __init__(
        self, parent, config_manager: ConfigManager, title="Settings", config_file="config.yaml"
    ):
        self.parent = parent
        self.config_manager = config_manager
        self.config_file = config_file
        self.result = None
        self.widgets = {}

        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center the dialog
        self.dialog.geometry(f"+{int(parent.winfo_rootx() + 50)}+{int(parent.winfo_rooty() + 50)}")

        self._create_widgets()

        # Handle window closing
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _create_widgets(self):
        """Create the settings dialog widgets."""
        # Main frame
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create tabs for each configuration category
        for category_name, category in self.config_manager._categories.items():
            self._create_category_tab(category_name, category)

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(button_frame, text="OK", command=self._on_ok).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self._on_cancel).pack(side=tk.RIGHT)

    def _create_category_tab(self, category_name: str, category):
        """Create a tab for a configuration category."""
        # Create tab frame
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text=category_name.title())

        # Create scrollable frame
        canvas = tk.Canvas(tab_frame)
        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Add parameters
        self._add_category_parameters(scrollable_frame, category_name, category)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _add_category_parameters(self, parent, category_name: str, category):
        """Add parameter widgets for a specific category."""
        row = 0
        parameters = category.get_parameters()

        for param in parameters:
            if param.required:
                # Skip required parameters as they are not configurable in GUI
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

            # Apply overrides to config manager
            self.config_manager._apply_kwargs(overrides)

            # Save to file
            self.config_manager.save_to_file(self.config_file)

            self.result = "ok"
            self.dialog.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {e}")

    def _on_cancel(self):
        """Handle Cancel button click."""
        self.result = "cancel"
        self.dialog.destroy()
