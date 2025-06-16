from ..config.config import ConfigParameterManager


NAME = "python_template_project"

"""
generate a gui application

pip install pyinstaller
pyinstaller --onefile --windowed python_template_project_gui.py
"""


class PythonProject:
    def __init__(
        self,
        config: ConfigParameterManager,
    ):
        self.input = getattr(config, "input")
        self.output = getattr(config, "output")
        self.min_dist = getattr(config, "min_dist")
        self.extract_waypoints = getattr(config, "extract_waypoints")
        self.date_format = getattr(config, "date_format")

        self.input = input

    def convert(self):
        print(
            f"Command run successfully: "
            f"{self.input}, "
            f"{self.date_format}, {self.min_dist}, {self.extract_waypoints}, {self.output}"
        )
