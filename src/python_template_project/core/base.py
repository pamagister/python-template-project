from python_template_project.config.config import ConfigParameterManager

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
        self.input = config.cli.input
        self.output = config.cli.output
        self.min_dist = config.cli.min_dist
        self.extract_waypoints = config.cli.extract_waypoints
        self.date_format = config.app.date_format

    def convert(self):
        print(
            f"Command run successfully: "
            f"{self.input}, "
            f"{self.date_format}, {self.min_dist}, {self.extract_waypoints}, {self.output}"
        )
