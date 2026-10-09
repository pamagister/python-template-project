from pathlib import Path

from config_cli_gui.docs import DocumentationGenerator

from python_template_project.config.config import ConfigParameterManager

"""function to generate config file and documentation."""


default_config: str = "config.yaml"
default_cli_doc: str = "docs/usage/cli.md"
default_config_doc: str = "docs/usage/config.md"

config_manager = ConfigParameterManager()

docGen = DocumentationGenerator(config_manager)
docGen.generate_default_config_file(output_file=default_config)
print(f"Generated: {default_config}")

docGen.generate_config_markdown_doc(output_file=default_config_doc)
print(f"Generated: {default_config_doc}")

docGen.generate_cli_markdown_doc(output_file=default_cli_doc, app_name=config_manager.get_app_name())
print(f"Generated: {default_cli_doc}")

additional_cli_content = """

# More parameter

For your specific projects that inherit from the library, 
you can add more parameters to the CLI and config file 
by creating your own ConfigManager subclass 
and adding more ConfigParameter instances. 
The documentation generator will automatically include them 
in the generated documentation.
"""

with Path(default_cli_doc).open("a", encoding="utf-8") as cli_doc:
    cli_doc.write(additional_cli_content)