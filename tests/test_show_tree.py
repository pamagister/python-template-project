import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "show_tree.py"


def run_tree(path, *args):
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(path), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout


def test_default_output_has_no_details(tmp_path):
    (tmp_path / "example.txt").write_text("hello", encoding="utf-8")

    output = run_tree(tmp_path)

    assert "[F] example.txt" in output
    assert "size:" not in output
    assert "modified:" not in output


def test_details_show_filesystem_metadata(tmp_path):
    (tmp_path / "example.txt").write_text("hello", encoding="utf-8")

    output = run_tree(tmp_path, "--details")

    assert "size: 5 B" in output
    assert re.search(r"modified: \d{4}-\d{2}-\d{2}", output)
    if os.name == "posix":
        assert "owner:" in output


def test_details_show_directory_entries(tmp_path):
    folder = tmp_path / "folder"
    folder.mkdir()
    (folder / "one.txt").write_text("1", encoding="utf-8")
    (folder / "two.txt").write_text("2", encoding="utf-8")

    output = run_tree(tmp_path, "--details")

    assert "entries: 2" in output


def test_details_read_ooxml_metadata(tmp_path):
    document = tmp_path / "report.docx"
    with zipfile.ZipFile(document, "w") as archive:
        archive.writestr(
            "docProps/core.xml",
            """<?xml version="1.0" encoding="UTF-8"?>
            <cp:coreProperties
                xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
                xmlns:dc="http://purl.org/dc/elements/1.1/"
                xmlns:dcterms="http://purl.org/dc/terms/">
                <dc:creator>Alice</dc:creator>
                <dc:title>Report</dc:title>
                <dcterms:created>2024-01-02T03:04:05Z</dcterms:created>
            </cp:coreProperties>""",
        )

    output = run_tree(tmp_path, "--details")

    assert "author: Alice" in output
    assert 'title: "Report"' in output
    assert "doc-created: 2024-01-02" in output


def test_details_read_odf_metadata(tmp_path):
    document = tmp_path / "report.odt"
    with zipfile.ZipFile(document, "w") as archive:
        archive.writestr(
            "meta.xml",
            """<?xml version="1.0" encoding="UTF-8"?>
            <office:document-meta
                xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0"
                xmlns:dc="http://purl.org/dc/elements/1.1/">
                <office:meta>
                    <meta:initial-creator>Bob</meta:initial-creator>
                    <dc:title>Bericht</dc:title>
                    <meta:creation-date>2024-02-03T04:05:06</meta:creation-date>
                </office:meta>
            </office:document-meta>""",
        )

    output = run_tree(tmp_path, "--details")

    assert "author: Bob" in output
    assert 'title: "Bericht"' in output
    assert "doc-created: 2024-02-03" in output


def test_details_read_pdf_metadata(tmp_path):
    document = tmp_path / "report.pdf"
    document.write_bytes(
        b"%PDF-1.4\n"
        b"1 0 obj\n"
        b"<< /Author (Alice) /Title (Report) /CreationDate (D:20240102030405Z) >>\n"
        b"endobj\n"
    )

    output = run_tree(tmp_path, "--details")

    assert "author: Alice" in output
    assert 'title: "Report"' in output
    assert "doc-created: 2024-01-02" in output


def test_folder_summary_shows_direct_child_counts(tmp_path):
    folder = tmp_path / "docs"
    folder.mkdir()
    (folder / "nested-a").mkdir()
    (folder / "nested-b").mkdir()
    (folder / "one.txt").write_text("12345", encoding="utf-8")
    (folder / "two.txt").write_text("1234567890", encoding="utf-8")

    output = run_tree(tmp_path, "--folder")

    assert "subfolders: 2" in output
    assert "files: 2" in output
    assert "size: 15 B" in output
    assert "types: 2 txt" in output


def test_folder_summary_shows_top_three_extensions(tmp_path):
    folder = tmp_path / "docs"
    folder.mkdir()
    for name in ["a.pdf", "b.PDF", "c.pdf", "d.docx", "e.DOCX", "f.xlsx", "g.csv"]:
        (folder / name).write_text("x", encoding="utf-8")

    output = run_tree(tmp_path, "--folder")

    assert "types: 3 pdf, 2 docx, 1 csv" in output


def test_folder_summary_labels_files_without_extension(tmp_path):
    folder = tmp_path / "docs"
    folder.mkdir()
    (folder / "README").write_text("x", encoding="utf-8")

    output = run_tree(tmp_path, "--folder")

    assert "types: 1 no ext" in output


def test_folder_mode_omits_file_details(tmp_path):
    (tmp_path / "example.txt").write_text("hello", encoding="utf-8")

    output = run_tree(tmp_path, "--folder")

    file_line = next(line for line in output.splitlines() if "[F] example.txt" in line)
    assert "[F] example.txt" in file_line
    assert "size:" not in file_line
    assert "modified:" not in file_line
    assert "author:" not in file_line


def test_folder_mode_wins_over_details(tmp_path):
    folder = tmp_path / "docs"
    folder.mkdir()
    (folder / "example.txt").write_text("hello", encoding="utf-8")

    output = run_tree(tmp_path, "--folder", "--details")

    folder_line = next(line for line in output.splitlines() if "[D] docs" in line)
    file_line = next(line for line in output.splitlines() if "[F] example.txt" in line)
    assert "subfolders: 0" in folder_line
    assert "files: 1" in folder_line
    assert "entries:" not in folder_line
    assert "size:" not in file_line
    assert "modified:" not in file_line
    assert "author:" not in file_line


def test_folder_summary_ignores_ignored_entries(tmp_path):
    folder = tmp_path / "docs"
    folder.mkdir()
    (folder / "visible.txt").write_text("hello", encoding="utf-8")
    (folder / "ignored.pyc").write_bytes(b"ignored")
    cache = folder / "__pycache__"
    cache.mkdir()
    (cache / "nested.pyc").write_bytes(b"ignored")

    output = run_tree(tmp_path, "--folder")

    folder_line = next(line for line in output.splitlines() if "[D] docs" in line)
    assert "subfolders: 0" in folder_line
    assert "files: 1" in folder_line
    assert "size: 5 B" in folder_line
    assert "types: 1 txt" in folder_line
