"""Image listing, thumbnail caching and export powered by Pillow."""

from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageOps

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tif", ".tiff"}

_FORMAT_ALIASES = {"jpg": "JPEG", "jpeg": "JPEG", "png": "PNG"}


def list_images(directory: str | Path) -> list[Path]:
    """Return image files directly inside ``directory``, skipping hidden entries."""
    directory = Path(directory)
    if not directory.is_dir():
        return []
    images = [
        entry
        for entry in sorted(directory.iterdir())
        if entry.is_file()
        and not entry.name.startswith(".")
        and entry.suffix.lower() in IMAGE_EXTENSIONS
    ]
    return images


def _thumbnail_cache_key(src: Path) -> str:
    """Build a cache key from name, size and mtime."""
    stat = src.stat()
    payload = f"{src.name}:{stat.st_size}:{int(stat.st_mtime)}"
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()


def thumbnail(src: str | Path, cache_dir: str | Path, max_size: int = 320) -> Path:
    """Return a cached thumbnail path, creating it when missing or stale."""
    src = Path(src)
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)

    target = cache_dir / f"{_thumbnail_cache_key(src)}_{max_size}.webp"
    if target.exists():
        return target

    with Image.open(src) as image:
        image = ImageOps.exif_transpose(image)
        image.thumbnail((max_size, max_size))
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGB")
        image.save(target, format="WEBP", quality=80)
    return target


def _unique_target(output_dir: Path, stem: str, suffix: str) -> Path:
    """Return a collision-free path inside ``output_dir``."""
    candidate = output_dir / f"{stem}{suffix}"
    counter = 1
    while candidate.exists():
        candidate = output_dir / f"{stem}_{counter}{suffix}"
        counter += 1
    return candidate


def export_images(
    files: list[str | Path],
    output_root: str | Path,
    fmt: str = "jpg",
    quality: int = 85,
    reduce: bool = False,
    max_side: int = 1200,
) -> tuple[Path, list[str]]:
    """Export images into a timestamped subfolder and return (dir, written paths)."""
    output_root = Path(output_root)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = output_root / f"export-{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    pil_format = _FORMAT_ALIASES.get(fmt.lower(), fmt.upper())
    suffix = ".jpg" if pil_format == "JPEG" else f".{fmt.lower()}"
    written: list[str] = []

    for file in files:
        src = Path(file)
        target = _unique_target(output_dir, src.stem, suffix)
        with Image.open(src) as image:
            image = ImageOps.exif_transpose(image)
            if reduce and max_side > 0:
                image = image.copy()
                image.thumbnail((max_side, max_side))
            if pil_format == "JPEG" and image.mode not in ("RGB", "L"):
                image = image.convert("RGB")
            save_kwargs: dict[str, object] = {}
            if pil_format == "JPEG":
                save_kwargs["quality"] = quality
            image.save(target, format=pil_format, **save_kwargs)
        written.append(str(target))

    return output_dir, written
