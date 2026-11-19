"""Tests for the in-repo configuration layer and doc generators."""

from pathlib import Path

import yaml

from python_template_project.config.config import build_default_config
from python_template_project.config.docgen import (
    generate_config_markdown,
    generate_default_config_file,
)


def test_defaults_match_expected_categories():
    config = build_default_config()
    assert set(config.categories) == {"app", "paths", "export", "server"}
    assert config.category("export").get("format").value == "jpg"
    assert config.category("export").get("jpg_quality").value == 85
    assert config.category("server").get("host").value == "127.0.0.1"


def test_set_and_get_roundtrip():
    config = build_default_config()
    config.set("export.format", "png")
    assert config.get("export", "format").value == "png"

    config.set("jpg_quality", "90")
    assert config.get("export", "jpg_quality").value == 90

    config.set("reduce_resolution", "true")
    assert config.get("export", "reduce_resolution").value is True


def test_set_unknown_key_raises():
    config = build_default_config()
    try:
        config.set("does_not_exist", 1)
    except KeyError:
        return
    raise AssertionError("Expected KeyError for unknown key")


def test_cli_grouping():
    config = build_default_config()
    export_cli = {parameter.flag for parameter in config.get_cli_parameters("export")}
    gui_cli = {parameter.flag for parameter in config.get_cli_parameters("gui")}
    assert {"source", "output", "format", "quality", "reduce", "max-side"} == export_cli
    assert {"host", "port", "open-browser"} == gui_cli
    assert config.get_cli_parameters(None) == []


def test_save_and_load_roundtrip(tmp_path):
    config = build_default_config()
    config.set("export.format", "png")
    config.set("server.port", "9000")

    path = tmp_path / "config.yaml"
    config.save(path)

    reloaded = build_default_config()
    reloaded.load(path)
    assert reloaded.get("export", "format").value == "png"
    assert reloaded.get("server", "port").value == 9000


def test_load_ignores_unknown_keys(tmp_path):
    path = tmp_path / "config.yaml"
    path.write_text(
        yaml.safe_dump({"export": {"format": "png", "unknown": 1}, "bogus": {}}),
        encoding="utf-8",
    )
    config = build_default_config()
    config.load(path)
    assert config.get("export", "format").value == "png"


def test_generate_default_config_has_comments(tmp_path):
    config = build_default_config()
    path = generate_default_config_file(config, tmp_path / "config.yaml")
    text = path.read_text(encoding="utf-8")
    assert "# Logging level for the application" in text
    assert "choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']" in text
    assert "format: 'jpg'" in text


def test_generated_config_is_stable(tmp_path):
    first = generate_default_config_file(build_default_config(), tmp_path / "a.yaml")
    second = generate_default_config_file(build_default_config(), tmp_path / "b.yaml")
    assert first.read_text(encoding="utf-8") == second.read_text(encoding="utf-8")


def test_generated_config_can_be_reloaded(tmp_path):
    config = build_default_config()
    path = generate_default_config_file(config, tmp_path / "config.yaml")

    reloaded = build_default_config()
    reloaded.load(path)
    assert reloaded.get("export", "jpg_quality").value == 85


def test_generate_config_markdown_lists_all(tmp_path):
    config = build_default_config()
    path = generate_config_markdown(config, tmp_path / "config.md")
    text = path.read_text(encoding="utf-8")
    for name in config.categories:
        assert f'## Category "{name}"' in text
    assert "jpg_quality" in text
    assert "127.0.0.1" in text
    assert Path(path).exists()
