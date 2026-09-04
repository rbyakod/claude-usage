from __future__ import annotations

import argparse
import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from core.db import connect, list_commands, list_usage, migrate, summary
from core.recommendations import recommendations_for


ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "app" / "static"
DEFAULT_DB = ROOT / "data" / "usage.sqlite3"
ROUTES = {"/", "/claude", "/codex", "/zai"}


def _provider_from_path(path: str, query: dict[str, list[str]]) -> str | None:
    if "provider" in query:
        return query["provider"][0]
    if path == "/claude":
        return "anthropic"
    if path == "/codex":
        return "codex"
    if path == "/zai":
        return "zai"
    return None


class UsageHandler(BaseHTTPRequestHandler):
    db_path = DEFAULT_DB

    def log_message(self, format: str, *args: object) -> None:
        return

    def _send_json(self, payload: object, status: int = 200) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html_shell(self) -> None:
        index = STATIC / "index.html"
        if index.exists():
            self._send_file(index)
            return
        body = b"<!doctype html><html><head><title>Usage Dashboards</title></head><body><main id=\"app\">Usage Dashboards</main></body></html>"
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path) -> None:
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        if parsed.path == "/api/summary":
            provider = _provider_from_path("", query)
            conn = connect(self.db_path)
            migrate(conn)
            payload = summary(conn, provider)
            conn.close()
            self._send_json(payload)
            return
        if parsed.path == "/api/recommendations":
            provider = _provider_from_path("", query)
            conn = connect(self.db_path)
            migrate(conn)
            commands = list_commands(conn, provider)
            usage = list_usage(conn, provider)
            conn.close()
            payload = [rec.__dict__ for rec in recommendations_for(commands, usage, _thresholds())]
            self._send_json({"provider": provider or "all", "recommendations": payload})
            return
        if parsed.path in ROUTES:
            self._send_html_shell()
            return
        static_path = (STATIC / parsed.path.lstrip("/")).resolve()
        if str(static_path).startswith(str(STATIC.resolve())) and static_path.exists() and static_path.is_file():
            self._send_file(static_path)
            return
        self._send_json({"error": "not_found"}, 404)


def _thresholds() -> dict[str, int]:
    path = ROOT / "config" / "thresholds.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def make_server(host: str, port: int, db_path: Path) -> ThreadingHTTPServer:
    class BoundHandler(UsageHandler):
        pass

    BoundHandler.db_path = db_path
    return ThreadingHTTPServer((host, port), BoundHandler)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Serve local usage dashboards.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=4310)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    args = parser.parse_args(argv)

    server = make_server(args.host, args.port, args.db)
    print(f"Serving usage dashboards on http://{args.host}:{args.port}/")
    print(f"Claude: http://{args.host}:{args.port}/claude")
    print(f"Codex: http://{args.host}:{args.port}/codex")
    print(f"Z.ai: http://{args.host}:{args.port}/zai")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
