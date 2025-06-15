import datetime
import mailbox
import os
import quopri
import re
from email.header import decode_header
from email.utils import mktime_tz, parsedate_tz



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
        output_format = getattr(config, "format")
        max_days = getattr(config, "max_days")
        date_format = getattr(config, "date_format")

        self.mbox_file = mbox_file
        self.include_options = {
            "from": include_from,
            "to": include_to,
            "date": include_date,
            "subject": include_subject,
        }


    def convert(self):
        print(f"Command run successfully: {self.mbox_file}")
