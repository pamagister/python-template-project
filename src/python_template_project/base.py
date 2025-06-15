NAME = "python_template_project"

"""
generate a gui application

pip install pyinstaller
pyinstaller --onefile --windowed python_template_project_gui.py

"""


class PythonProject:
    def __init__(
        self,
        config,
    ):
        mbox_file = getattr(config, "mbox_file")
        include_from = getattr(config, "sent_from")
        include_to = getattr(config, "to")
        include_date = getattr(config, "date")
        include_subject = getattr(config, "subject")

        self.mbox_file = mbox_file
        self.include_options = {
            "from": include_from,
            "to": include_to,
            "date": include_date,
            "subject": include_subject,
        }

    def convert(self):
        print(f"Command run successfully: {self.mbox_file}")
