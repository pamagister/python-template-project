"""Generic unittest class for testing mbox_converter CLI and config integration.

This test suite validates the integration between parameters.py, config.py, and cli.py
with various parameter combinations and edge cases.
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
import yaml

from src.python_template_project.config import ConfigParameterManager
from src.python_template_project.parameters import PARAMETERS
from src.python_template_project import cli


class TestGenericCLI(unittest.TestCase):
    """Generic test class for CLI and config integration."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

        # Create a dummy mbox file for testing
        self.dummy_mbox = self.temp_path / "test.mbox"
        self.dummy_mbox.write_text("dummy mbox content")

        # Default config for testing
        self.default_config = {param.name: param.default for param in PARAMETERS}

    def tearDown(self):
        """Clean up after each test method."""
        self.temp_dir.cleanup()

    def test_parameter_definitions_consistency(self):
        """Test that all parameters are properly defined and consistent."""
        parameter_names = [param.name for param in PARAMETERS]

        # Check for duplicate parameter names
        self.assertEqual(
            len(parameter_names),
            len(set(parameter_names)),
            "Duplicate parameter names found",
        )

        # Validate each parameter
        for param in PARAMETERS:
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

    def test_config_manager_initialization_defaults(self):
        """Test ConfigParameterManager initialization with default values."""
        config = ConfigParameterManager()

        for param in PARAMETERS:
            with self.subTest(parameter=param.name):
                self.assertTrue(hasattr(config, param.name))
                self.assertEqual(getattr(config, param.name), param.default)

    def test_config_manager_initialization_with_kwargs(self):
        """Test ConfigParameterManager initialization with keyword arguments."""
        test_kwargs = {
            "sent_from": False,
            "format": "csv",
            "max_days": 30,
            "subject": False,
        }

        config = ConfigParameterManager(**test_kwargs)

        for key, expected_value in test_kwargs.items():
            with self.subTest(parameter=key):
                self.assertEqual(getattr(config, key), expected_value)

    def test_config_file_yaml_loading(self):
        """Test loading configuration from YAML file."""
        yaml_config = {
            "sent_from": False,
            "format": "csv",
            "max_days": 7,
            "subject": True,
        }

        yaml_file = self.temp_path / "test_config.yaml"
        with open(yaml_file, "w") as f:
            yaml.dump(yaml_config, f)

        config = ConfigParameterManager(config_file=str(yaml_file))

        for key, expected_value in yaml_config.items():
            with self.subTest(parameter=key):
                self.assertEqual(getattr(config, key), expected_value)

    def test_config_file_json_loading(self):
        """Test loading configuration from JSON file."""
        json_config = {"to": False, "date": True, "format": "txt", "max_days": 14}

        json_file = self.temp_path / "test_config.json"
        with open(json_file, "w") as f:
            json.dump(json_config, f)

        config = ConfigParameterManager(config_file=str(json_file))

        for key, expected_value in json_config.items():
            with self.subTest(parameter=key):
                self.assertEqual(getattr(config, key), expected_value)

    def test_config_file_not_found(self):
        """Test handling of non-existent config file."""
        non_existent_file = self.temp_path / "does_not_exist.yaml"

        with self.assertRaises(FileNotFoundError):
            ConfigParameterManager(config_file=str(non_existent_file))

    def test_config_to_dict(self):
        """Test conversion of config to dictionary."""
        config = ConfigParameterManager(sent_from=False, format="csv")
        config_dict = config.to_dict()

        self.assertIsInstance(config_dict, dict)
        self.assertEqual(len(config_dict), len(PARAMETERS))

        for param in PARAMETERS:
            with self.subTest(parameter=param.name):
                self.assertIn(param.name, config_dict)

    def test_config_save_to_yaml_file(self):
        """Test saving configuration to YAML file."""
        config = ConfigParameterManager(sent_from=False, format="csv", max_days=30)

        output_file = self.temp_path / "output_config.yaml"
        config.save_to_file(str(output_file), format_="yaml")

        self.assertTrue(output_file.exists())

        # Load and verify saved config
        with open(output_file, "r") as f:
            saved_config = yaml.safe_load(f)

        self.assertEqual(saved_config["sent_from"], False)
        self.assertEqual(saved_config["format"], "csv")
        self.assertEqual(saved_config["max_days"], 30)

    def test_config_save_to_json_file(self):
        """Test saving configuration to JSON file."""
        config = ConfigParameterManager(to=False, date=True, subject=False)

        output_file = self.temp_path / "output_config.json"
        config.save_to_file(str(output_file), format_="json")

        self.assertTrue(output_file.exists())

        # Load and verify saved config
        with open(output_file, "r") as f:
            saved_config = json.load(f)

        self.assertEqual(saved_config["to"], False)
        self.assertEqual(saved_config["date"], True)
        self.assertEqual(saved_config["subject"], False)

    def test_generate_default_config_file(self):
        """Test generation of default configuration file."""
        output_file = self.temp_path / "default_config.yaml"

        ConfigParameterManager.generate_default_config_file(str(output_file))

        self.assertTrue(output_file.exists())

        # Check file content
        content = output_file.read_text()
        self.assertIn("# Configuration File", content)

        for param in PARAMETERS:
            with self.subTest(parameter=param.name):
                self.assertIn(param.name, content)
                self.assertIn(param.help, content)

    def test_parameter_type_validation(self):
        """Test parameter type validation and conversion."""
        test_cases = [
            ("sent_from", True, bool),
            ("sent_from", False, bool),
            ("format", "txt", str),
            ("format", "csv", str),
            ("max_days", -1, int),
            ("max_days", 30, int),
        ]

        for param_name, value, expected_type in test_cases:
            with self.subTest(parameter=param_name, value=value):
                config = ConfigParameterManager(**{param_name: value})
                actual_value = getattr(config, param_name)
                self.assertIsInstance(actual_value, expected_type)
                self.assertEqual(actual_value, value)

    def test_parameter_choices_validation(self):
        """Test parameter choices validation."""
        # Find parameters with choices
        choice_params = [param for param in PARAMETERS if param.choices]

        for param in choice_params:
            with self.subTest(parameter=param.name):
                # Test valid choices
                for choice in param.choices:
                    config = ConfigParameterManager(**{param.name: choice})
                    self.assertEqual(getattr(config, param.name), choice)

    def test_all_parameter_combinations(self):
        """Test various combinations of parameters."""
        test_combinations = [
            {"sent_from": False, "to": False},
            {"format": "csv", "max_days": 30},
            {"date": True, "subject": False, "format": "txt"},
            {
                "sent_from": True,
                "to": True,
                "date": True,
                "subject": True,
                "format": "csv",
                "max_days": 7,
            },
        ]

        for combination in test_combinations:
            with self.subTest(combination=combination):
                config = ConfigParameterManager(**combination)

                for key, expected_value in combination.items():
                    self.assertEqual(getattr(config, key), expected_value)

                # Ensure other parameters have default values
                for param in PARAMETERS:
                    if param.name not in combination:
                        self.assertEqual(getattr(config, param.name), param.default)

    def test_config_override_precedence(self):
        """Test that CLI arguments override config file values."""
        # Create config file
        config_file_data = {"format": "txt", "max_days": 10, "sent_from": True}
        config_file = self.temp_path / "precedence_test.yaml"

        with open(config_file, "w") as f:
            yaml.dump(config_file_data, f)

        # Create config with file, then override with kwargs
        config = ConfigParameterManager(
            config_file=str(config_file),
            format="csv",  # Override
            subject=False,  # New value
        )

        # Check overrides worked
        self.assertEqual(config.format, "csv")  # Overridden
        self.assertEqual(config.subject, False)  # New value
        self.assertEqual(config.max_days, 10)  # From file
        self.assertEqual(config.sent_from, True)  # From file

    def test_generate_cli_markdown_doc(self):
        """Test generation of CLI markdown documentation."""
        output_file = self.temp_path / "cli_doc_test.md"

        ConfigParameterManager.generate_cli_markdown_doc(str(output_file))

        self.assertTrue(output_file.exists())

        content = output_file.read_text(encoding="utf8")
        self.assertIn("# Command line interface", content)

        # Check that parameters are documented
        cli_params = [param for param in PARAMETERS if param.is_cli]
        for param in cli_params:
            with self.subTest(parameter=param.name):
                if param.name != "mbox_file":  # Positional arg handled differently
                    self.assertIn(f"--{param.name}", content)


if __name__ == "__main__":
    # Run with verbose output
    unittest.main(verbosity=2)
