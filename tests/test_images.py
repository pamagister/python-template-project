"""Tests for the Pillow-based image engine."""

from pathlib import Path

from PIL import Image

from python_template_project.core.images import export_images, list_images, thumbnail

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def _make_image(path: Path, size=(40, 30), color=(200, 30, 30)) -> Path:
    Image.new("RGB", size, color).save(path)
    return path


def test_list_images_filters_and_skips_hidden(tmp_path):
    _make_image(tmp_path / "a.jpg")
    _make_image(tmp_path / "b.PNG")
    (tmp_path / "notes.txt").write_text("x", encoding="utf-8")
    (tmp_path / ".hidden.jpg").write_text("x", encoding="utf-8")
    sub = tmp_path / "sub"
    sub.mkdir()
    _make_image(sub / "c.jpg")

    images = list_images(tmp_path)
    names = {image.name for image in images}
    assert names == {"a.jpg", "b.PNG"}


def test_list_images_missing_dir(tmp_path):
    assert list_images(tmp_path / "nope") == []


def test_thumbnail_is_cached(tmp_path):
    src = _make_image(tmp_path / "a.jpg")
    cache = tmp_path / "cache"
    first = thumbnail(src, cache)
    assert first.exists()
    mtime = first.stat().st_mtime_ns
    second = thumbnail(src, cache)
    assert second == first
    assert second.stat().st_mtime_ns == mtime


def test_thumbnail_invalidates_on_change(tmp_path):
    src = _make_image(tmp_path / "a.jpg")
    cache = tmp_path / "cache"
    first = thumbnail(src, cache)
    first_bytes = first.read_bytes()
    _make_image(src, size=(41, 30), color=(1, 2, 3))
    second = thumbnail(src, cache)
    assert second != first
    assert second.read_bytes() != first_bytes


def test_export_applies_resize_and_collisions(tmp_path):
    src = _make_image(tmp_path / "a.jpg", size=(100, 50))
    output_root = tmp_path / "out"
    output_dir, written = export_images([src, src], output_root, fmt="jpg", quality=80)
    assert output_dir.parent == output_root
    assert output_dir.name.startswith("export-")
    assert len(written) == 2
    assert written[0] != written[1]
    with Image.open(written[0]) as image:
        assert image.size == (100, 50)

    resized_dir, resized = export_images([src], output_root, fmt="jpg", reduce=True, max_side=40)
    with Image.open(resized[0]) as image:
        assert max(image.size) <= 40


def test_export_png_format(tmp_path):
    src = _make_image(tmp_path / "a.jpg")
    _, written = export_images([src], tmp_path / "out", fmt="png")
    assert written[0].endswith(".png")
    with Image.open(written[0]) as image:
        assert image.format == "PNG"


def test_examples_are_listed():
    images = list_images(EXAMPLES)
    assert images, "expected example images for smoke testing"
