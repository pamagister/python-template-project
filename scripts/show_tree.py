import argparse
import ast
import inspect
import os
import re
import sys
import zipfile
from collections import Counter
from datetime import datetime
from xml.etree import ElementTree

# Stellen Sie sicher, dass stdout UTF-8 verwendet, damit Unicode-Symbole
# (Emojis, Baum-Zeichen) auch unter Windows (Standardkodierung cp1252)
# ohne UnicodeEncodeError ausgegeben werden können.
if sys.stdout is not None and getattr(sys.stdout, "encoding", None) != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError, ValueError):
        pass

# Symbole
FOLDER_SYMBOL = "📁"
FILE_SYMBOL = "◼️"  # "📋"
IMAGE_SYMBOL = "🖼️"
DOCUMENT_SYMBOL = "📝"
CLASS_SYMBOL = "🏛️"
FUNC_SYMBOL = "⚙️"
ATTR_SYMBOL = "🔹"
BRANCH = "├── "
LAST_BRANCH = "└── "
VERTICAL_LINE = "│   "
INDENT = "    "

# Ignorieren
IGNORE_DIRS = {
    ".pytest_cache",
    ".git",
    ".ruff",
    ".venv",
    ".github",
    "build",
    "dist",
    ".idea",
    "htmlcov",
    "__pycache__",
    "__main__",
    "site",
}
IGNORE_EXTENSIONS = {".pyc"}

# Dateitypen
IMAGE_EXTENSIONS = {
    ".avif",
    ".bmp",
    ".gif",
    ".heic",
    ".heif",
    ".ico",
    ".jpeg",
    ".jpg",
    ".png",
    ".svg",
    ".tif",
    ".tiff",
    ".webp",
}

# Dokument-Metadaten
ODF_EXTENSIONS = {".odg", ".odp", ".ods", ".odt"}
OOXML_EXTENSIONS = {".docx", ".pptx", ".xlsx"}
PDF_EXTENSIONS = {".pdf"}
DOCUMENT_EXTENSIONS = (
    ODF_EXTENSIONS
    | OOXML_EXTENSIONS
    | PDF_EXTENSIONS
    | {".doc", ".docm", ".epub", ".ppt", ".pptm", ".rtf", ".xls", ".xlsm"}
)
MAX_AUTHOR_LENGTH = 40
MAX_TITLE_LENGTH = 60

ODF_NAMESPACES = {
    "dc": "http://purl.org/dc/elements/1.1/",
    "meta": "urn:oasis:names:tc:opendocument:xmlns:meta:1.0",
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
}
OOXML_NAMESPACES = {
    "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
}

PDF_INFO_PATTERN = re.compile(
    rb"/(Author|Title|CreationDate)\s*(?:<([0-9A-Fa-f\s]+)>|\(((?:\\.|[^\\()])*)\))",
    re.DOTALL,
)
PDF_ESCAPE_PATTERN = re.compile(rb"\\(?:([nrtbf()\\])|([0-7]{1,3})|(?:\r\n|\r|\n))")
PDF_ESCAPE_MAP = {
    b"n": b"\n",
    b"r": b"\r",
    b"t": b"\t",
    b"b": b"\b",
    b"f": b"\f",
    b"(": b"(",
    b")": b")",
    b"\\": b"\\",
}


def should_ignore(path):
    name = os.path.basename(path)
    if name in IGNORE_DIRS:
        return True
    if os.path.isfile(path):
        ext = os.path.splitext(path)[1]
        return ext in IGNORE_EXTENSIONS
    return False


def format_function_signature(func_node):
    """Erzeugt die Signatur einer Funktion als String"""
    args = []
    for arg in func_node.args.args:
        arg_str = arg.arg
        if arg.annotation:
            arg_str += f": {ast.unparse(arg.annotation)}"
        args.append(arg_str)
    if func_node.args.vararg:
        args.append(f"*{func_node.args.vararg.arg}")
    if func_node.args.kwarg:
        args.append(f"**{func_node.args.kwarg.arg}")
    args_str = ", ".join(args)
    ret = ""
    if func_node.returns:
        ret = f" -> {ast.unparse(func_node.returns)}"
    return f"{func_node.name}({args_str}){ret}"


def parse_python_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            node = ast.parse(f.read(), filename=file_path)
    except Exception:
        return []

    structure = []
    for child in node.body:
        if isinstance(child, ast.ClassDef):
            class_entry = {"type": "class", "name": child.name, "attributes": [], "methods": []}

            for item in child.body:
                if isinstance(item, ast.FunctionDef):
                    sig = format_function_signature(item)
                    class_entry["methods"].append(sig)
                elif isinstance(item, ast.Assign):
                    # Klassenattribute
                    for target in item.targets:
                        if isinstance(target, ast.Name):
                            class_entry["attributes"].append(target.id)
                elif isinstance(item, ast.AnnAssign):
                    if isinstance(item.target, ast.Name):
                        class_entry["attributes"].append(item.target.id)

                # Instanzattribute aus Methoden
                if isinstance(item, ast.FunctionDef):
                    for stmt in ast.walk(item):
                        if isinstance(stmt, ast.Assign):
                            for target in stmt.targets:
                                if (
                                    isinstance(target, ast.Attribute)
                                    and isinstance(target, ast.Name)
                                    and target.id == "self"
                                ):
                                    class_entry["attributes"].append(target.attr)
                        elif isinstance(stmt, ast.AnnAssign):
                            if (
                                isinstance(stmt.target, ast.Attribute)
                                and isinstance(stmt.target, ast.Name)
                                and stmt.target.id == "self"
                            ):
                                class_entry["attributes"].append(stmt.target.attr)

            structure.append(class_entry)

        elif isinstance(child, ast.FunctionDef):
            sig = format_function_signature(child)
            structure.append({"type": "function", "signature": sig})

    return structure


def format_size(size):
    """Formatiert eine Dateigroesse lesbar."""
    value = float(size)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            if unit == "B":
                return f"{int(value)} B"
            return f"{value:.0f} {unit}"
        value /= 1024
    return f"{int(value)} B"


def format_timestamp(timestamp):
    """Formatiert einen Zeitstempel als Jahr-Monat-Tag."""
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")


def format_iso_date(value):
    """Extrahiert ein ISO-Datum aus einem Metadatenwert."""
    match = re.match(r"(\d{4})-(\d{2})-(\d{2})", value)
    return match.group(0) if match else None


def format_pdf_date(value):
    """Wandelt ein PDF-Datum (D:YYYYMMDD...) in YYYY-MM-DD um."""
    match = re.match(r"D:(\d{4})(\d{2})(\d{2})", value)
    if not match:
        return None
    return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"


def shorten_text(value, limit):
    """Kuerzt Metadatenwerte fuer die kompakte Baumausgabe."""
    value = value.replace('"', "'").strip()
    if len(value) > limit:
        return value[: limit - 3].rstrip() + "..."
    return value


def unescape_pdf_string(value):
    """Loest PDF-Escapes in einem Literal-String auf."""

    def replace(match):
        simple = match.group(1)
        if simple:
            return PDF_ESCAPE_MAP[simple]
        octal = match.group(2)
        if octal:
            return bytes([int(octal, 8) & 0xFF])
        return b""

    return PDF_ESCAPE_PATTERN.sub(replace, value)


def decode_pdf_string(value):
    """Dekodiert einen PDF-String als UTF-16 oder Latin-1."""
    value = unescape_pdf_string(value)
    if value.startswith(b"\xfe\xff"):
        text = value[2:].decode("utf-16-be", errors="ignore")
    elif value.startswith(b"\xff\xfe"):
        text = value[2:].decode("utf-16-le", errors="ignore")
    else:
        text = value.decode("latin-1", errors="replace")
    text = re.sub(r"[\x00-\x1f\x7f]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def is_plausible_text(text):
    """Filtert offensichtliche Binaerdaten aus PDF-Metadaten."""
    if not text:
        return False
    printable = sum(1 for char in text if char.isprintable())
    return printable / len(text) >= 0.9


def extract_pdf_metadata(path):
    """Liest Author, Titel und Erstellungsdatum best-effort aus PDF-Infos."""
    try:
        with open(path, "rb") as file:
            data = file.read()
    except OSError:
        return {}

    metadata = {}
    seen = set()
    for match in PDF_INFO_PATTERN.finditer(data):
        key = match.group(1).decode("ascii")
        if key in seen:
            continue

        raw = match.group(2)
        if raw is not None:
            try:
                raw = bytes.fromhex(re.sub(rb"\s+", b"", raw).decode("ascii"))
            except (UnicodeDecodeError, ValueError):
                continue
        else:
            raw = match.group(3)

        text = decode_pdf_string(raw)
        if not is_plausible_text(text):
            continue

        if key == "Author":
            metadata["author"] = shorten_text(text, MAX_AUTHOR_LENGTH)
            seen.add(key)
        elif key == "Title":
            metadata["title"] = shorten_text(text, MAX_TITLE_LENGTH)
            seen.add(key)
        elif key == "CreationDate":
            created = format_pdf_date(text)
            if created:
                metadata["doc-created"] = created
                seen.add(key)

    return metadata


def read_zip_xml(path, member):
    """Liest eine XML-Datei aus einem ZIP-Container."""
    try:
        with zipfile.ZipFile(path) as archive:
            return ElementTree.fromstring(archive.read(member))
    except (
        KeyError,
        NotImplementedError,
        OSError,
        RuntimeError,
        ValueError,
        zipfile.BadZipFile,
        ElementTree.ParseError,
    ):
        return None


def find_text(root, path, namespaces):
    """Liest den Text eines XML-Elements, falls vorhanden."""
    if root is None:
        return None
    element = root.find(path, namespaces)
    if element is None or not element.text:
        return None
    return element.text.strip()


def extract_odf_metadata(path):
    """Liest Metadaten aus einer OpenDocument-Datei."""
    root = read_zip_xml(path, "meta.xml")
    if root is None:
        return {}

    author = find_text(root, "office:meta/meta:initial-creator", ODF_NAMESPACES)
    author = author or find_text(root, "office:meta/dc:creator", ODF_NAMESPACES)
    title = find_text(root, "office:meta/dc:title", ODF_NAMESPACES)
    created = find_text(root, "office:meta/meta:creation-date", ODF_NAMESPACES)
    created = created or find_text(root, "office:meta/dc:date", ODF_NAMESPACES)

    metadata = {}
    if author:
        metadata["author"] = shorten_text(author, MAX_AUTHOR_LENGTH)
    if title:
        metadata["title"] = shorten_text(title, MAX_TITLE_LENGTH)
    if created:
        created_date = format_iso_date(created)
        if created_date:
            metadata["doc-created"] = created_date
    return metadata


def extract_ooxml_metadata(path):
    """Liest Metadaten aus einer Office-Open-XML-Datei."""
    root = read_zip_xml(path, "docProps/core.xml")
    if root is None:
        return {}

    author = find_text(root, "dc:creator", OOXML_NAMESPACES)
    author = author or find_text(root, "cp:lastModifiedBy", OOXML_NAMESPACES)
    title = find_text(root, "dc:title", OOXML_NAMESPACES)
    created = find_text(root, "dcterms:created", OOXML_NAMESPACES)

    metadata = {}
    if author:
        metadata["author"] = shorten_text(author, MAX_AUTHOR_LENGTH)
    if title:
        metadata["title"] = shorten_text(title, MAX_TITLE_LENGTH)
    if created:
        created_date = format_iso_date(created)
        if created_date:
            metadata["doc-created"] = created_date
    return metadata


def get_document_metadata(path):
    """Waehlt anhand der Endung den passenden Metadaten-Leser."""
    extension = os.path.splitext(path)[1].lower()
    if extension in PDF_EXTENSIONS:
        return extract_pdf_metadata(path)
    if extension in ODF_EXTENSIONS:
        return extract_odf_metadata(path)
    if extension in OOXML_EXTENSIONS:
        return extract_ooxml_metadata(path)
    return {}


def get_owner(stat_result):
    """Ermittelt den Besitzernamen aus einem stat-Ergebnis."""
    try:
        import pwd
    except ImportError:
        return None
    try:
        return pwd.getpwuid(stat_result.st_uid).pw_name
    except KeyError:
        return str(stat_result.st_uid)


def get_file_extension(name):
    """Ermittelt die Dateiendung ohne Punkt, case-insensitiv."""
    extension = os.path.splitext(name)[1].lower()
    return extension[1:] if extension else "no ext"


def get_file_symbol(name):
    """Waehlt anhand der Dateiendung das passende Dateisymbol."""
    extension = os.path.splitext(name)[1].lower()
    if extension in IMAGE_EXTENSIONS:
        return IMAGE_SYMBOL
    if extension in DOCUMENT_EXTENSIONS:
        return DOCUMENT_SYMBOL
    return FILE_SYMBOL


def format_type_counts(extensions, limit=3):
    """Formatiert die haeufigsten Dateitypen."""
    top_extensions = sorted(extensions.items(), key=lambda item: (-item[1], item[0]))[:limit]
    if not top_extensions:
        return "-"
    return ", ".join(f"{count} {extension}" for extension, count in top_extensions)


def format_folder_summary(path):
    """Erzeugt eine kompakte Zusammenfassung der direkten Ordnerkinder."""
    try:
        items = os.listdir(path)
    except OSError:
        return ""

    subfolders = 0
    files = 0
    total_size = 0
    extensions = Counter()

    for item in items:
        full_path = os.path.join(path, item)
        if should_ignore(full_path):
            continue
        if os.path.isdir(full_path):
            subfolders += 1
            continue

        files += 1
        try:
            total_size += os.path.getsize(full_path)
        except OSError:
            pass

        extensions[get_file_extension(item)] += 1

    parts = [
        f"subfolders: {subfolders}",
        f"files: {files}",
        f"size: {format_size(total_size)}",
        f"types: {format_type_counts(extensions)}",
    ]

    return f"  [{', '.join(parts)}]"


def collect_tree_stats(path):
    """Sammelt rekursiv Ordner-, Datei- und Typstatistiken."""
    stats = {"folders": 0, "files": 0, "size": 0, "extensions": Counter()}
    try:
        items = os.listdir(path)
    except OSError:
        return stats

    for item in items:
        full_path = os.path.join(path, item)
        if should_ignore(full_path):
            continue
        if os.path.isdir(full_path):
            stats["folders"] += 1
            child_stats = collect_tree_stats(full_path)
            stats["folders"] += child_stats["folders"]
            stats["files"] += child_stats["files"]
            stats["size"] += child_stats["size"]
            stats["extensions"].update(child_stats["extensions"])
        else:
            stats["files"] += 1
            try:
                stats["size"] += os.path.getsize(full_path)
            except OSError:
                pass
            stats["extensions"][get_file_extension(item)] += 1

    return stats


def format_tree_summary(path):
    """Erzeugt die immer sichtbare Gesamtzusammenfassung."""
    stats = collect_tree_stats(path)
    parts = [
        f"folders: {stats['folders']}",
        f"files: {stats['files']}",
        f"size: {format_size(stats['size'])}",
        f"types: {format_type_counts(stats['extensions'])}",
    ]
    return f"\nSummary: [{', '.join(parts)}]"


def format_details(path, is_dir):
    """Erzeugt den kompakten Metadaten-Suffix fuer eine Baumzeile."""
    if is_dir:
        return format_folder_summary(path)

    try:
        stat_result = os.stat(path)
    except OSError:
        return ""

    parts = [f"size: {format_size(stat_result.st_size)}"]

    birthtime = getattr(stat_result, "st_birthtime", None)
    if birthtime is not None:
        parts.append(f"created: {format_timestamp(birthtime)}")
    parts.append(f"modified: {format_timestamp(stat_result.st_mtime)}")

    owner = get_owner(stat_result)
    if owner:
        parts.append(f"owner: {owner}")

    metadata = get_document_metadata(path)
    if metadata.get("author"):
        parts.append(f"author: {metadata['author']}")
    if metadata.get("title"):
        parts.append(f'title: "{metadata["title"]}"')
    if metadata.get("doc-created"):
        parts.append(f"doc-created: {metadata['doc-created']}")

    return f"  [{', '.join(parts)}]"


def show_tree(path, prefix="", show_code=False, show_details=False, show_folders_only=False):
    try:
        items = sorted(os.listdir(path))
    except PermissionError:
        return

    items = [i for i in items if not should_ignore(os.path.join(path, i))]
    if show_folders_only:
        items = [i for i in items if os.path.isdir(os.path.join(path, i))]

    for index, item in enumerate(items):
        full_path = os.path.join(path, item)
        is_last = index == len(items) - 1
        is_dir = os.path.isdir(full_path)
        connector = LAST_BRANCH if is_last else BRANCH
        symbol = FOLDER_SYMBOL if is_dir else get_file_symbol(item)

        details = format_details(full_path, is_dir) if show_details else ""
        print(f"{prefix}{connector}{symbol} {item}{details}")
        next_prefix = prefix + (INDENT if is_last else VERTICAL_LINE)
        if is_dir:
            show_tree(full_path, next_prefix, show_code, show_details, show_folders_only)
        elif show_code and item.endswith(".py"):
            code_structure = parse_python_file(full_path)
            for entry in code_structure:
                if entry["type"] == "class":
                    # Attribute
                    attr_str = ', '.join(entry["attributes"]) if entry["attributes"] else "None"

                    print(f"{next_prefix}{BRANCH}{CLASS_SYMBOL} {entry['name']} - {ATTR_SYMBOL}: {attr_str}")
                    sub_prefix = next_prefix + VERTICAL_LINE

                    # Methoden mit Signatur
                    for method in entry["methods"]:
                        print(f"{sub_prefix}{BRANCH}{FUNC_SYMBOL} {entry['name']}.{method}")

                elif entry["type"] == "function":
                    print(f"{next_prefix}{BRANCH}{FUNC_SYMBOL} {entry['signature']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Shows directory and Python code structure as a tree."
    )
    parser.add_argument("path", nargs="?", default=".", help="Start directory")
    parser.add_argument(
        "--show-code",
        action="store_true",
        default=False,
        help="Shows functions, classes and attributes in .py files",
    )
    parser.add_argument(
        "--details",
        action="store_true",
        default=False,
        help="Shows file metadata and per-folder summaries",
    )
    parser.add_argument(
        "--folder",
        action="store_true",
        default=False,
        help="Shows only directories and hides file names",
    )
    args = parser.parse_args()

    show_tree(
        args.path,
        show_code=args.show_code,
        show_details=args.details,
        show_folders_only=args.folder,
    )
    print(format_tree_summary(args.path))

    print('\nSymbol description:')
    print(f"{FOLDER_SYMBOL} - Directory")
    print(f"{FILE_SYMBOL} - File")
    print(f"{IMAGE_SYMBOL} - Image")
    print(f"{DOCUMENT_SYMBOL} - Document")
    print(f"{CLASS_SYMBOL} - Class")
    print(f"{FUNC_SYMBOL} - Function/Method")
    print(f"{ATTR_SYMBOL} - Attribute")
    print(args)
