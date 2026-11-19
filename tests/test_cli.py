"""Tests for the argparse CLI and its documentation generator."""

from pathlib import Path

import pytest

from python_template_project.cli.cli import build_parser, main
from python_template_project.cli.docgen import generate_cli_markdown
from python_template_project.config.config import build_default_config


def test_help_lists_subcommands(capsys):
    with pytest.raises(SystemExit) as exit_info:
        main(["--help"])
    assert exit_info.value.code == 0
    out = capsys.readouterr().out
    for command in ("gui", "export", "config"):
        assert command in out


@pytest.mark.parametrize("command", ["gui", "export", "config"])
def test_subcommand_help(command, capsys):
    with pytest.raises(SystemExit) as exit_info:
        main([command, "--help"])
    assert exit_info.value.code == 0
    assert command in capsys.readouterr().out or "usage" in capsys.readouterr().out


def test_export_parses_overrides():
    config = build_default_config()
    parser = build_parser(config)
    args = parser.parse_args(["export", "--source", "/tmp/in", "--format", "png", "--reduce"])
    assert args.source_dir == "/tmp/in"
    assert args.format == "png"
    assert args.reduce_resolution is True


def test_gui_parses_open_browser_toggle():
    config = build_default_config()
    parser = build_parser(config)
    args = parser.parse_args(["gui", "--no-open-browser", "--port", "9999"])
    assert args.open_browser is False
    assert args.port == 9999


def test_config_set_persists(tmp_path, monkeypatch):
    config_path = tmp_path / "config.yaml"
    monkeypatch.chdir(tmp_path)
    code = main(["--config", str(config_path), "config", "--set", "export.format=png"])
    assert code == 0
    assert "format: png" in config_path.read_text(encoding="utf-8")

    code = main(["--config", str(config_path), "config", "--show"])
    assert code == 0


def test_config_path_prints(tmp_path, capsys):
    config_path = tmp_path / "config.yaml"
    main(["--config", str(config_path), "config", "--path"])
    assert str(config_path) in capsys.readouterr().out


def test_generate_cli_markdown(tmp_path):
    config = build_default_config()
    parser = build_parser(config)
    output = generate_cli_markdown(parser, tmp_path / "cli.md")
    text = Path(output).read_text(encoding="utf-8")
    assert "`python-template-project`" in text
    assert "`python-template-project gui`" in text
    assert "`python-template-project export`" in text
    assert "`python-template-project config`" in text
    assert "--source" in text
