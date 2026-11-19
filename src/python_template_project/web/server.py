"""Local, dependency-free web UI for browsing and exporting images.

The server is built on :class:`http.server.ThreadingHTTPServer` and only ever
binds to the loopback interface by default. It exposes a small JSON API plus
the static single-page app under ``web/assets``.
"""

from __future__ import annotations

import json
import mimetypes
import threading
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from python_template_project.config.config import ConfigManager
from python_template_project.core.images import export_images, list_images, thumbnail
from python_template_project.core.logging import initialize_logging
from python_template_project.core.paths import resolve_output_root

ASSETS_DIR = Path(__file__).resolve().parent / "assets"
READTHEDOCS_URL = "https://python-template-project.readthedocs.io/en/stable/"


class WebApp:
    """Holds shared state and implements the JSON API operations."""

    def __init__(self, config: ConfigManager, cache_dir: Path):
        self.config = config
        self.cache_dir = cache_dir
        self.logger = initialize_logging(config).get_logger("web")
        self._lock = threading.Lock()

    def images(self, path: str) -> dict:
        """Return image tiles with thumbnail URLs for a directory."""
        directory = Path(path).expanduser()
        tiles = []
        for image in list_images(directory):
            tiles.append(
                {
                    "name": image.name,
                    "path": str(image),
                    "thumbnail": f"/api/thumb?path={image}",
                }
            )
        return {"path": str(directory), "images": tiles}

    def browse(self, path: str) -> dict:
        """Return subdirectories of ``path`` for the directory browser."""
        directory = Path(path).expanduser()
        if not directory.is_dir():
            return {"path": str(directory), "parent": None, "directories": []}
        directories = sorted(
            (
                entry
                for entry in directory.iterdir()
                if entry.is_dir() and not entry.name.startswith(".")
            ),
            key=lambda entry: entry.name.lower(),
        )
        parent = str(directory.parent) if directory.parent != directory else None
        return {
            "path": str(directory),
            "parent": parent,
            "directories": [entry.name for entry in directories],
        }

    def config_payload(self) -> dict:
        """Return the configuration as nested dictionaries."""
        return {name: category.as_dict() for name, category in self.config.categories.items()}

    def update_config(self, values: dict) -> dict:
        """Apply a nested configuration update and persist it."""
        with self._lock:
            for category_name, category_values in values.items():
                if not isinstance(category_values, dict):
                    continue
                for name, value in category_values.items():
                    try:
                        self.config.set(f"{category_name}.{name}", value)
                    except KeyError:
                        self.logger.warning(
                            "Ignoring unknown config key %s.%s", category_name, name
                        )
            self.config.save()
        return self.config_payload()

    def run_export(self, payload: dict) -> dict:
        """Export the requested images and return the result summary."""
        files = payload.get("files") or []
        export = self.config.category("export")
        paths = self.config.category("paths")
        output_root = resolve_output_root(payload.get("output") or paths.get("output_root").value)
        output_dir, written = export_images(
            files,
            output_root,
            fmt=payload.get("format", export.get("format").value),
            quality=int(payload.get("quality", export.get("jpg_quality").value)),
            reduce=bool(payload.get("reduce", export.get("reduce_resolution").value)),
            max_side=int(payload.get("max_side", export.get("max_long_side").value)),
        )
        return {"output_dir": str(output_dir), "files": written}


class RequestHandler(BaseHTTPRequestHandler):
    """Serve the static app and the JSON API."""

    server_version = "python-template-project"

    @property
    def app(self) -> WebApp:
        """Return the shared application state."""
        return self.server.app  # type: ignore[attr-defined]

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        """Route HTTP access logs through the application logger."""
        self.app.logger.debug("%s - %s", self.address_string(), format % args)

    def _send_json(self, payload: object, status: int = HTTPStatus.OK) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path, content_type: str | None = None) -> None:
        if not path.is_file():
            self._send_json({"error": "not found"}, HTTPStatus.NOT_FOUND)
            return
        data = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header(
            "Content-Type",
            content_type or mimetypes.guess_type(path.name)[0] or "application/octet-stream",
        )
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _query(self) -> dict[str, str]:
        return {key: values[0] for key, values in parse_qs(urlparse(self.path).query).items()}

    def do_GET(self) -> None:  # noqa: N802
        """Handle GET requests for static assets and API reads."""
        route = urlparse(self.path).path
        if route == "/" or route == "/index.html":
            self._send_file(ASSETS_DIR / "index.html", "text/html; charset=utf-8")
            return
        if route.startswith("/static/"):
            name = route[len("/static/") :]
            self._send_file(ASSETS_DIR / name)
            return
        if route == "/api/images":
            path = self._query().get("path", "")
            if not path:
                self._send_json({"error": "missing path"}, HTTPStatus.BAD_REQUEST)
                return
            self._send_json(self.app.images(path))
            return
        if route == "/api/thumb":
            path = self._query().get("path", "")
            if not path:
                self._send_json({"error": "missing path"}, HTTPStatus.BAD_REQUEST)
                return
            thumb = thumbnail(path, self.app.cache_dir)
            self._send_file(thumb, "image/webp")
            return
        if route == "/api/browse":
            path = self._query().get("path", "")
            self._send_json(self.app.browse(path))
            return
        if route == "/api/config":
            self._send_json(self.app.config_payload())
            return
        if route == "/api/logs":
            limit = int(self._query().get("limit", "200"))
            self._send_json({"logs": self.app.logger and _recent_logs(self.app, limit)})
            return
        self._send_json({"error": "not found"}, HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802
        """Handle POST requests for config updates and exports."""
        route = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw or b"{}")
        except json.JSONDecodeError:
            self._send_json({"error": "invalid JSON"}, HTTPStatus.BAD_REQUEST)
            return

        if route == "/api/config":
            self._send_json(self.app.update_config(payload))
            return
        if route == "/api/export":
            try:
                self._send_json(self.app.run_export(payload))
            except Exception as error:  # pragma: no cover - defensive
                self.app.logger.error("Export failed: %s", error)
                self._send_json({"error": str(error)}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return
        self._send_json({"error": "not found"}, HTTPStatus.NOT_FOUND)


def _recent_logs(app: WebApp, limit: int) -> list[str]:
    """Return recent log lines from the logging ring buffer."""
    from python_template_project.core.logging import get_logger_manager

    return get_logger_manager().recent_logs(limit)


def make_server(
    config: ConfigManager, host: str | None = None, port: int | None = None
) -> ThreadingHTTPServer:
    """Create (but do not start) the HTTP server."""
    server_category = config.category("server")
    host = host or server_category.get("host").value
    port = int(port or server_category.get("port").value)
    cache_dir = Path(config.config_file).resolve().parent / ".thumbcache"
    app = WebApp(config, cache_dir)
    httpd = ThreadingHTTPServer((host, port), RequestHandler)
    httpd.app = app  # type: ignore[attr-defined]
    return httpd


def run_server(config: ConfigManager, host: str | None = None, port: int | None = None) -> int:
    """Start the web server, optionally opening the browser."""
    httpd = make_server(config, host, port)
    actual_host, actual_port = httpd.server_address[:2]
    if config.category("server").get("open_browser").value:
        webbrowser.open(f"http://{actual_host}:{actual_port}/")
    print(
        f"Serving python-template-project on http://{actual_host}:{actual_port}/ (Ctrl+C to stop)"
    )
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
    return 0
