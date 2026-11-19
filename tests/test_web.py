"""Integration tests for the local web UI server."""

import json
import threading
import urllib.request
from pathlib import Path

import pytest
from PIL import Image

from python_template_project.config.config import build_default_config
from python_template_project.web.server import make_server


@pytest.fixture
def images_dir(tmp_path):
    directory = tmp_path / "images"
    directory.mkdir()
    for index in range(2):
        Image.new("RGB", (40, 30), (index * 50, 20, 20)).save(directory / f"img{index}.jpg")
    (directory / "notes.txt").write_text("x", encoding="utf-8")
    return directory


@pytest.fixture
def server(tmp_path, images_dir):
    config = build_default_config()
    config.set("paths.source_dir", str(images_dir))
    config.set("paths.output_root", str(tmp_path / "out"))
    config.set("server.host", "127.0.0.1")
    config.set("server.port", "0")
    config.config_file = tmp_path / "config.yaml"

    httpd = make_server(config)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    host, port = httpd.server_address[:2]
    base = f"http://{host}:{port}"
    try:
        yield base, config, images_dir
    finally:
        httpd.shutdown()
        httpd.server_close()


def get(base, path):
    with urllib.request.urlopen(base + path) as response:
        return response.status, response.read(), response.headers.get("Content-Type", "")


def post(base, path, payload):
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        base + path, data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(request) as response:
        return response.status, json.loads(response.read())


def test_index_and_static(server):
    base, _, _ = server
    status, body, _ = get(base, "/")
    assert status == 200
    assert b"python-template-project" in body

    status, body, content_type = get(base, "/static/app.js")
    assert status == 200
    assert "javascript" in content_type


def test_images_and_thumbnails(server):
    base, _, images_dir = server
    import urllib.parse

    status, body, _ = get(base, "/api/images?path=" + urllib.parse.quote(str(images_dir)))
    data = json.loads(body)
    assert status == 200
    assert len(data["images"]) == 2

    thumb_path = data["images"][0]["thumbnail"]
    status, body, content_type = get(base, thumb_path)
    assert status == 200
    assert content_type == "image/webp"
    assert body[:4] == b"RIFF"


def test_browse_lists_directories(tmp_path, server):
    base, _, images_dir = server
    import urllib.parse

    (images_dir / "sub").mkdir()
    status, body, _ = get(base, "/api/browse?path=" + urllib.parse.quote(str(images_dir)))
    data = json.loads(body)
    assert status == 200
    assert "sub" in data["directories"]


def test_config_roundtrip(server):
    base, _, _ = server
    status, body, _ = get(base, "/api/config")
    assert status == 200
    assert "export" in json.loads(body)

    status, payload = post(base, "/api/config", {"export": {"format": "png"}})
    assert status == 200
    assert payload["export"]["format"] == "png"


def test_export_endpoint(server):
    base, _, images_dir = server
    import urllib.parse

    _, body, _ = get(base, "/api/images?path=" + urllib.parse.quote(str(images_dir)))
    paths = [image["path"] for image in json.loads(body)["images"]]

    status, result = post(base, "/api/export", {"files": paths, "format": "png"})
    assert status == 200
    assert len(result["files"]) == 2
    assert Path(result["output_dir"]).exists()


def test_logs_endpoint(server):
    base, _, _ = server
    status, body, _ = get(base, "/api/logs")
    assert status == 200
    assert "logs" in json.loads(body)


def test_unknown_route_404(server):
    base, _, _ = server
    with pytest.raises(urllib.error.HTTPError) as error:
        get(base, "/api/nope")
    assert error.value.code == 404
