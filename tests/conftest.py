from __future__ import annotations

import socket
import threading
import time
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "ghost-test/1.0"
    sys_version = ""

    def log_message(self, *args: object) -> None:
        pass

    def do_GET(self) -> None:
        if self.path == "/slow":
            time.sleep(3)
            return
        if self.path == "/endless":
            # Advertises a huge body but sends almost none; a body read would hang.
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length", str(10**9))
            self.end_headers()
            self.wfile.write(b"x" * 16)
            self.wfile.flush()
            time.sleep(3)
            return
        if self.path == "/redirect":
            self.send_response(302)
            self.send_header("Location", "/?token=abc123")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        body = b"<html>hi</html>" if self.path == "/html" else b'{"ok": true}'
        ctype = {
            "/html": "text/html; charset=utf-8",
            "/problem": "application/problem+json",
            "/none": None,
        }.get(self.path, "application/json; charset=utf-8")
        self.send_response(404 if self.path == "/missing" else 200)
        if ctype:
            self.send_header("Content-Type", ctype)
        self.send_header("Set-Cookie", "sid=supersecret")
        self.send_header("X-Api-Key", "topsecret")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class QuietServer(ThreadingHTTPServer):
    daemon_threads = True

    def handle_error(self, request: object, client_address: object) -> None:
        pass


@pytest.fixture
def http_server() -> Iterator[int]:
    server = QuietServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield server.server_address[1]
    server.shutdown()
    server.server_close()


@pytest.fixture
def raw_server() -> Iterator[int]:
    """A listener that speaks garbage instead of HTTP."""
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    sock.listen(5)
    stop = threading.Event()

    def serve() -> None:
        sock.settimeout(0.2)
        while not stop.is_set():
            try:
                conn, _ = sock.accept()
            except OSError:
                continue
            try:
                conn.sendall(b"\x00\x01 not http\r\n\r\n")
            except OSError:
                pass
            finally:
                conn.close()

    threading.Thread(target=serve, daemon=True).start()
    yield sock.getsockname()[1]
    stop.set()
    sock.close()


@pytest.fixture
def closed_port() -> int:
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port
