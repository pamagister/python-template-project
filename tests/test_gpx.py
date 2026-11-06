import shutil
import zipfile
from datetime import datetime
from pathlib import Path

import gpxpy
import pytest
from gpxpy.gpx import GPXTrackPoint

from python_template_project.config.config import ConfigParameterManager
from python_template_project.core.logging import initialize_logging
from src.python_template_project.core.base import BaseGPXProcessor

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def test_paths(tmp_path):
    """Provide common paths and a temp output directory."""
    current_test_file_dir = Path(__file__).parent
    test_gpx_file = current_test_file_dir.parent / "examples" / "kuhkopfsteig.gpx"

    output_dir = tmp_path / "output"
    output_dir.mkdir(exist_ok=True)

    logger = initialize_logging(ConfigParameterManager()).get_logger("TestGPXProcessor")

    processor = BaseGPXProcessor(
        input_=str(test_gpx_file),
        output=str(output_dir),
        logger=logger,
    )

    return {
        "test_gpx_file": test_gpx_file,
        "output_dir": output_dir,
        "logger": logger,
        "processor": processor,
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_get_output_folder(test_paths):
    logger = test_paths["logger"]
    test_gpx_file = test_paths["test_gpx_file"]

    processor_with_output = BaseGPXProcessor(
        input_=str(test_gpx_file),
        output="custom_output",
        logger=logger,
    )
    output_path = processor_with_output._get_output_folder()
    assert output_path == Path("custom_output")
    assert output_path.exists()
    shutil.rmtree(output_path)

    processor_no_output = BaseGPXProcessor(input_=str(test_gpx_file), logger=logger)
    output_path_default = processor_no_output._get_output_folder()
    assert str(output_path_default).startswith(str(Path.cwd() / "gpx_processed_"))
    assert output_path_default.exists()
    shutil.rmtree(output_path_default)


def test_get_adjusted_elevation(test_paths):
    processor = test_paths["processor"]

    test_point = GPXTrackPoint(latitude=50.91605, longitude=14.07259, elevation=100.0)
    adjusted = processor._get_adjusted_elevation(test_point)

    assert isinstance(adjusted, int)
    assert 124 < adjusted < 400
    assert adjusted != 100

    test_point_no_elev = GPXTrackPoint(latitude=50.91605, longitude=14.07259)
    adjusted2 = processor._get_adjusted_elevation(test_point_no_elev)

    assert isinstance(adjusted2, int)
    assert 124 < adjusted2 < 400


def test_calculate_distance(test_paths):
    processor = test_paths["processor"]

    p1 = GPXTrackPoint(latitude=50.91605, longitude=14.07259)
    p2 = GPXTrackPoint(latitude=50.91695, longitude=14.07360)

    distance = processor._calculate_distance(p1, p2)
    assert abs(distance - 122.59003627960) < 1

    # same point → distance = 0
    p_same = GPXTrackPoint(latitude=50.0, longitude=10.0)
    assert processor._calculate_distance(p_same, p_same) == 0.0


def test_optimize_track_points(test_paths):
    processor = test_paths["processor"]

    points = [
        GPXTrackPoint(50.0, 10.0, 100.0, datetime.now()),
        GPXTrackPoint(50.00001, 10.00001, 101.0, datetime.now()),
        GPXTrackPoint(50.00002, 10.00002, 102.0, datetime.now()),
        GPXTrackPoint(50.00010, 10.00010, 103.0, datetime.now()),
        GPXTrackPoint(50.00020, 10.00020, 104.0, datetime.now()),
        GPXTrackPoint(50.00030, 10.00030, 105.0, datetime.now()),
    ]

    original_min = processor.min_dist
    processor.min_dist = 20.0

    optimized = processor._optimize_track_points(points)
    assert len(optimized) == 3

    for p in optimized:
        assert p.time is None
        assert p.latitude == round(float(p.latitude), 5)
        assert p.longitude == round(float(p.longitude), 5)
        assert isinstance(p.elevation, int)

    processor.min_dist = original_min


def test_get_input_files(test_paths):
    processor = test_paths["processor"]
    test_gpx_file = test_paths["test_gpx_file"]
    output_dir = test_paths["output_dir"]
    logger = test_paths["logger"]

    # single file
    files_single = processor._get_input_files()
    assert len(files_single) == 1
    assert files_single[0] == test_gpx_file

    # directory containing GPX files
    temp_dir = output_dir / "temp_gpx_dir"
    temp_dir.mkdir()
    (temp_dir / "test1.gpx").touch()
    (temp_dir / "test2.gpx").touch()
    (temp_dir / "not_gpx.txt").touch()

    proc_dir = BaseGPXProcessor(input_=str(temp_dir), logger=logger)
    files_dir = proc_dir._get_input_files()
    assert len(files_dir) == 2
    assert any(f.name == "test1.gpx" for f in files_dir)
    assert any(f.name == "test2.gpx" for f in files_dir)

    # ZIP file case
    temp_zip = output_dir / "test.zip"
    with zipfile.ZipFile(temp_zip, "w") as zf:
        zf.writestr("zip1.gpx", "<gpx></gpx>")
        zf.writestr("zip2.gpx", "<gpx></gpx>")
        zf.writestr("not_gpx.txt", "bad")

    proc_zip = BaseGPXProcessor(input_=str(temp_zip), logger=logger)
    files_zip = proc_zip._get_input_files()
    assert len(files_zip) == 2
    assert any(f.name == "zip1.gpx" for f in files_zip)
    assert any(f.name == "zip2.gpx" for f in files_zip)


def test_load_gpx_file(test_paths):
    processor = test_paths["processor"]
    output_dir = test_paths["output_dir"]
    test_gpx_file = test_paths["test_gpx_file"]

    gpx_obj = processor._load_gpx_file(test_gpx_file)
    assert gpx_obj is not None
    assert isinstance(gpx_obj, gpxpy.gpx.GPX)
    assert len(gpx_obj.tracks) > 0

    gpx_none = processor._load_gpx_file(Path("nonexistent.gpx"))
    assert gpx_none is None

    malformed = output_dir / "malformed.gpx"
    malformed.write_text("<gpx><track><segment><point></point></segment></track>")
    assert processor._load_gpx_file(malformed) is None


def test_save_gpx_file(test_paths):
    processor = test_paths["processor"]
    output_dir = test_paths["output_dir"]

    gpx_obj = gpxpy.gpx.GPX()
    gpx_obj.name = "Test Save"

    out_file = output_dir / "saved_test.gpx"
    processor._save_gpx_file(gpx_obj, out_file)

    assert out_file.exists()

    reloaded = gpxpy.parse(open(out_file, "r", encoding="utf-8"))
    assert reloaded.name == "Test Save"


def test_compress_files(test_paths):
    test_gpx_file = test_paths["test_gpx_file"]
    output_dir = test_paths["output_dir"]
    processor = test_paths["processor"]

    shutil.rmtree(output_dir)
    output_dir.mkdir()

    compressed_path = output_dir / f"compressed_{test_gpx_file.name}"

    processor.compress_files()
    assert compressed_path.exists()

    compressed_gpx = gpxpy.parse(open(compressed_path, "r", encoding="utf-8"))
    original_gpx = gpxpy.parse(open(test_gpx_file, "r", encoding="utf-8"))

    orig_pts = sum(len(s.points) for t in original_gpx.tracks for s in t.segments)
    cmp_pts = sum(len(s.points) for t in compressed_gpx.tracks for s in t.segments)

    assert cmp_pts < orig_pts
    assert cmp_pts < orig_pts * 0.5
    assert compressed_gpx.time is None
    assert not bool(compressed_gpx.extensions)


def test_merge_files(test_paths):
    output_dir = test_paths["output_dir"]
    logger = test_paths["logger"]
    test_gpx_file = test_paths["test_gpx_file"]

    # create dummy gpx
    dummy_path = output_dir / "dummy.gpx"
    dummy_gpx = gpxpy.gpx.GPX()
    track = gpxpy.gpx.GPXTrack()
    segment = gpxpy.gpx.GPXTrackSegment()
    segment.points.append(GPXTrackPoint(51.0, 14.0, 100))
    segment.points.append(GPXTrackPoint(51.0001, 14.0001, 101))
    track.segments.append(segment)
    dummy_gpx.tracks.append(track)
    dummy_path.write_text(dummy_gpx.to_xml())

    merge_dir = output_dir / "merge_input"
    merge_dir.mkdir()
    shutil.copy(test_gpx_file, merge_dir)
    shutil.copy(dummy_path, merge_dir)

    processor = BaseGPXProcessor(
        input_=str(merge_dir),
        output=str(output_dir),
        logger=logger,
    )
    processor.merge_files()

    merged_path = output_dir / "merged_tracks.gpx"
    assert merged_path.exists()

    merged = gpxpy.parse(open(merged_path, "r", encoding="utf-8"))

    assert len(merged.tracks) == 2

    names = [t.name for t in merged.tracks]
    assert any("kuhkopfsteig" in (n or "").lower() for n in names)
    assert any("dummy" in (n or "").lower() for n in names)

    merged_cnt = sum(len(s.points) for t in merged.tracks for s in t.segments)
    orig_kuh = gpxpy.parse(open(test_gpx_file, "r", encoding="utf-8"))
    orig_kuh_cnt = sum(len(s.points) for t in orig_kuh.tracks for s in t.segments)
    orig_dummy_cnt = sum(len(s.points) for t in dummy_gpx.tracks for s in t.segments)

    assert merged_cnt < orig_kuh_cnt + orig_dummy_cnt
    assert merged_cnt > 0


def test_extract_pois(test_paths):
    processor = test_paths["processor"]
    output_dir = test_paths["output_dir"]

    processor.extract_pois()

    poi_file = output_dir / "extracted_pois.gpx"
    assert poi_file.exists()

    poi_gpx = gpxpy.parse(open(poi_file, "r", encoding="utf-8"))

    assert len(poi_gpx.waypoints) == 1

    poi = poi_gpx.waypoints[0]
    assert poi.name.startswith("POI_")
    assert "Start of" in poi.description
    assert poi.type == "Track Start"
    assert isinstance(poi.latitude, float)
    assert isinstance(poi.longitude, float)
    assert isinstance(poi.elevation, float)
