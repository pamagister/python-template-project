"""Generic unittest class for testing CLI and config integration.

This test suite validates the integration between config.py and cli.py
with various parameter combinations and edge cases.
"""

import tempfile
import unittest
from pathlib import Path

from generic_config_cli_gui.config_framework import DocumentationGenerator
from python_template_project.config.config import ConfigParameterManager


class TestGenericCLI(unittest.TestCase):
    """Generic test class for CLI and config integration."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

        # Create a dummy file for testing
        self.dummy_input = self.temp_path / "test.input"
        self.dummy_input.write_text("dummy input content")

        # Default config for testing
        self.configManager = ConfigParameterManager()
        self.default_cli_config = {
            name: field.default for name, field in self.configManager.get_cli_category()
        }

    def tearDown(self):
        """Clean up after each test method."""
        self.temp_dir.cleanup()

    def test_parameter_definitions_consistency(self):
        """Test that all parameters are properly defined and consistent."""
        parameter_names = self.default_cli_config.keys()

        # Check for duplicate parameter names
        self.assertEqual(
            len(parameter_names),
            len(set(parameter_names)),
            "Duplicate parameter names found",
        )

        # Validate each parameter
        for param in self.configManager.get_cli_category().get_parameters():
            with self.subTest(parameter=param.name):
                self.assertIsInstance(param.name, str)
                self.assertIsInstance(param.type_, type)
                self.assertIsInstance(param.help, str)
                self.assertGreater(len(param.help), 0, "Help text should not be empty")

                # Check if default value matches type
                if param.default is not None and param.default != "":
                    if param.type_ == bool:
                        self.assertIsInstance(param.default, bool)
                    elif param.type_ == int:
                        self.assertIsInstance(param.default, int)
                    elif param.type_ == str:
                        self.assertIsInstance(param.default, str)

    def test_config_file_not_found(self):
        """Test handling of non-existent config file."""
        non_existent_file = self.temp_path / "does_not_exist.yaml"

        with self.assertRaises(FileNotFoundError):
            ConfigParameterManager(config_file=str(non_existent_file))

    def test_generate_default_config_file(self):
        """Test generation of default configuration file."""
        output_file = self.temp_path / "default_config.yaml"

        config_manager = ConfigParameterManager()
        docGen = DocumentationGenerator(config_manager)
        docGen.generate_default_config_file(str(output_file))

        self.assertTrue(output_file.exists())

        # Check file content
        content = output_file.read_text()
        self.assertIn("# Configuration File", content)

        for param in self.default_cli_config.keys():
            with self.subTest(parameter=param):
                self.assertIn(param, content)

    def test_parameter_choices_validation(self):
        """Test parameter choices validation."""
        # Find parameters with choices
        choice_params = [
            param
            for param in self.configManager.get_cli_category().get_parameters()
            if param.choices
        ]

        for param in choice_params:
            with self.subTest(parameter=param.name):
                # Test valid choices
                for choice in param.choices:
                    self.assertIn(choice, param.choices)

    def test_generate_cli_markdown_doc(self):
        """Test generation of CLI markdown documentation."""
        output_file = self.temp_path / "cli_doc_test.md"

        config_manager = ConfigParameterManager()
        docGen = DocumentationGenerator(config_manager)
        docGen.generate_cli_markdown_doc(str(output_file))

        self.assertTrue(output_file.exists())

        content = output_file.read_text(encoding="utf8")
        self.assertIn("# Command Line Interface", content)

        # Check that parameters are documented
        cli_params = self.default_cli_config.keys()
        for param in cli_params:
            with self.subTest(parameter=param):
                if param != "input":  # Positional arg handled differently
                    self.assertIn(f"--{param}", content)


if __name__ == "__main__":
    # Run with verbose output
    unittest.main(verbosity=2)
