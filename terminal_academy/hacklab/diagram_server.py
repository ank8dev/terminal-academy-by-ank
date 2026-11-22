"""A tiny web server (standard library only) that shows the live diagram.

It serves one page (``diagram.html``) and pushes updates to it with
Server-Sent Events (SSE). SSE is the simplest way for a server to push: the
browser opens ``/events`` once and keeps it open, and the server writes
``data: {...}\\n\\n`` whenever the picture changes. No WebSocket library, no
polling from the browser.

How the pieces fit:

    LabSession.snapshot()  ->  one poller thread turns it into JSON
                           ->  every open /events connection streams the JSON
                           ->  diagram.html draws it as SVG

Everything here is stdlib: ``http.server`` + ``threading`` + ``json``.
"""

from __future__ import annotations

import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable, Dict, Optional

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
DIAGRAM_HTML = os.path.join(PACKAGE_DIR, "diagram.html")

# How often the poller asks the session for a fresh snapshot.
POLL_INTERVAL = 1.0


class DiagramServer:
    """Serves the diagram page and streams live state to it."""

    def __init__(self, state_provider: Callable[[], Dict[str, Any]],
                 host: str = "127.0.0.1", port: int = 0) -> None:
        self.state_provider = state_provider
        self.host = host
        self._latest_json = "{}"
        self.version = 0
        self._stop = threading.Event()
        self._lock = threading.Condition()
        self._httpd = ThreadingHTTPServer((host, port), self._make_handler())
        self._httpd.daemon_threads = True
        self.port = self._httpd.server_address[1]
        self._server_thread: Optional[threading.Thread] = None
        self._poll_thread: Optional[threading.Thread] = None

    @property
    def url(self) -> str:
        return "http://%s:%d/" % (self.host, self.port)

    # ----- lifecycle ------------------------------------------------------

    def start(self) -> str:
        self._server_thread = threading.Thread(target=self._httpd.serve_forever,
                                                name="diagram-http", daemon=True)
        self._server_thread.start()
        self._poll_thread = threading.Thread(target=self._poll_loop,
                                              name="diagram-poll", daemon=True)
        self._poll_thread.start()
        return self.url

    def stop(self) -> None:
        self._stop.set()
        with self._lock:
            self._lock.notify_all()
        try:
            self._httpd.shutdown()
            self._httpd.server_close()
        except Exception:
            pass

    # ----- the poller -----------------------------------------------------

    def _poll_loop(self) -> None:
        while not self._stop.is_set():
            try:
                state = self.state_provider()
                payload = json.dumps(state)
            except Exception as exc:  # never let the diagram take the app down
                payload = json.dumps({"error": str(exc)})
            if payload != self._latest_json:
                with self._lock:
                    self._latest_json = payload
                    self.version += 1
                    self._lock.notify_all()
            self._stop.wait(POLL_INTERVAL)

    def latest(self) -> str:
        return self._latest_json

    # ----- the HTTP handler ----------------------------------------------

    def _make_handler(self):
        server = self

        class Handler(BaseHTTPRequestHandler):
            # Quiet: do not print a line for every request.
            def log_message(self, *args: Any) -> None:
                pass

            def do_GET(self) -> None:
                path = self.path.split("?", 1)[0]
                if path == "/":
                    self._serve_page()
                elif path == "/state":
                    self._serve_state()
                elif path == "/events":
                    self._serve_events()
                else:
                    self.send_error(404, "Not found")

            def _serve_page(self) -> None:
                try:
                    with open(DIAGRAM_HTML, "rb") as fh:
                        body = fh.read()
                except OSError:
                    self.send_error(500, "diagram.html missing")
                    return
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def _serve_state(self) -> None:
                body = server.latest().encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def _serve_events(self) -> None:
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Connection", "keep-alive")
                self.end_headers()
                last_sent = -1
                try:
                    while not server._stop.is_set():
                        with server._lock:
                            if server.version == last_sent:
                                # Wait for a change, but wake up now and then to
                                # send a comment so the connection stays alive.
                                server._lock.wait(timeout=15.0)
                            payload = server._latest_json
                            version = server.version
                        if version != last_sent:
                            last_sent = version
                            self.wfile.write(b"data: " + payload.encode("utf-8") + b"\n\n")
                        else:
                            self.wfile.write(b": keep-alive\n\n")  # SSE comment
                        self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError, ValueError):
                    pass  # the browser tab closed; just end this stream

        return Handler
