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
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout


def get_line(output, marker):
    return next(line for line in output.splitlines() if marker in line)


def test_default_output_has_no_entry_details(tmp_path):
    (tmp_path / "example.txt").write_text("hello", encoding="utf-8")

    output = run_tree(tmp_path)

    assert "◼️ example.txt" in output
    assert "◼️ example.txt  [" not in output
    assert "modified:" not in output
    assert "Summary:" in output


def test_default_output_uses_file_type_symbols(tmp_path):
    (tmp_path / "photo.JPG").write_text("x", encoding="utf-8")
    (tmp_path / "sheet.xlsx").write_text("x", encoding="utf-8")
    (tmp_path / "letter.odt").write_text("x", encoding="utf-8")
    (tmp_path / "report.pdf").write_text("x", encoding="utf-8")
    (tmp_path / "notes.md").write_text("x", encoding="utf-8")

    output = run_tree(tmp_path)

    assert "🖼️ photo.JPG" in output
    assert "📝 sheet.xlsx" in output
    assert "📝 letter.odt" in output
    assert "📝 report.pdf" in output
    assert "◼️ notes.md" in output


def test_default_output_includes_recursive_summary(tmp_path):
    folder = tmp_path / "docs"
    folder.mkdir()
    (folder / "one.pdf").write_text("x", encoding="utf-8")
    (folder / "two.pdf").write_text("xy", encoding="utf-8")

    output = run_tree(tmp_path)

    assert "Summary: [folders: 1, files: 2, size: 3 B, types: 2 pdf]" in output


def test_details_show_filesystem_metadata(tmp_path):
    (tmp_path / "example.txt").write_text("hello", encoding="utf-8")

    output = run_tree(tmp_path, "--details")

    file_line = get_line(output, "◼️ example.txt")
    assert "size: 5 B" in file_line
    assert re.search(r"modified: \d{4}-\d{2}-\d{2}", file_line)
    if os.name == "posix":
        assert "owner:" in file_line


def test_details_show_folder_summary(tmp_path):
    folder = tmp_path / "docs"
    folder.mkdir()
    (folder / "nested-a").mkdir()
    (folder / "nested-b").mkdir()
    (folder / "one.txt").write_text("12345", encoding="utf-8")
    (folder / "two.txt").write_text("1234567890", encoding="utf-8")

    output = run_tree(tmp_path, "--details")

    folder_line = get_line(output, "📁 docs")
    assert "subfolders: 2" in folder_line
    assert "files: 2" in folder_line
    assert "size: 15 B" in folder_line
    assert "types: 2 txt" in folder_line
    assert "entries:" not in folder_line


def test_details_show_top_three_extensions(tmp_path):
    folder = tmp_path / "docs"
    folder.mkdir()
    for name in ["a.pdf", "b.PDF", "c.pdf", "d.docx", "e.DOCX", "f.xlsx", "g.csv"]:
        (folder / name).write_text("x", encoding="utf-8")

    output = run_tree(tmp_path, "--details")

    folder_line = get_line(output, "📁 docs")
    assert "types: 3 pdf, 2 docx, 1 csv" in folder_line


def test_details_label_files_without_extension(tmp_path):
    folder = tmp_path / "docs"
    folder.mkdir()
    (folder / "README").write_text("x", encoding="utf-8")

    output = run_tree(tmp_path, "--details")

    folder_line = get_line(output, "📁 docs")
    assert "types: 1 no ext" in folder_line


def test_folder_mode_hides_file_names(tmp_path):
    (tmp_path / "secret.txt").write_text("hello", encoding="utf-8")
    folder = tmp_path / "docs"
    folder.mkdir()
    (folder / "hidden.pdf").write_text("x", encoding="utf-8")

    output = run_tree(tmp_path, "--folder")
    tree_output = output.split("\nSummary:", 1)[0]

    assert "📁 docs" in tree_output
    assert "◼️" not in tree_output
    assert "🖼️" not in tree_output
    assert "📝" not in tree_output
    assert "secret.txt" not in tree_output
    assert "hidden.pdf" not in tree_output
    assert "Summary: [folders: 1, files: 2, size: 6 B, types: 1 pdf, 1 txt]" in output


def test_folder_mode_with_details_shows_folder_summary_only(tmp_path):
    folder = tmp_path / "docs"
    folder.mkdir()
    (folder / "nested").mkdir()
    (folder / "example.txt").write_text("hello", encoding="utf-8")

    output = run_tree(tmp_path, "--folder", "--details")
    tree_output = output.split("\nSummary:", 1)[0]

    assert "◼️" not in tree_output
    assert "🖼️" not in tree_output
    assert "📝" not in tree_output
    assert "example.txt" not in tree_output
    folder_line = get_line(tree_output, "📁 docs")
    assert "subfolders: 1" in folder_line
    assert "files: 1" in folder_line
    assert "size: 5 B" in folder_line
    assert "types: 1 txt" in folder_line


def test_folder_mode_without_details_has_no_folder_summary(tmp_path):
    folder = tmp_path / "docs"
    folder.mkdir()
    (folder / "example.txt").write_text("hello", encoding="utf-8")

    output = run_tree(tmp_path, "--folder")

    folder_line = get_line(output, "📁 docs")
    assert "subfolders:" not in folder_line
    assert "files:" not in folder_line
    assert "types:" not in folder_line


def test_folder_summary_ignores_ignored_entries(tmp_path):
    folder = tmp_path / "docs"
    folder.mkdir()
    (folder / "visible.txt").write_text("hello", encoding="utf-8")
    (folder / "ignored.pyc").write_bytes(b"ignored")
    cache = folder / "__pycache__"
    cache.mkdir()
    (cache / "nested.pyc").write_bytes(b"ignored")

    output = run_tree(tmp_path, "--folder", "--details")

    folder_line = get_line(output, "📁 docs")
    assert "subfolders: 0" in folder_line
    assert "files: 1" in folder_line
    assert "size: 5 B" in folder_line
    assert "types: 1 txt" in folder_line


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
