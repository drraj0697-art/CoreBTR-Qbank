#!/usr/bin/env python3
"""Serve the standalone QBank as a correctly named HTML attachment."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
HTML_FILE = ROOT / "CoreBTR Qbank converted.html"
PORT = 8000


class DownloadHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        route = urlsplit(self.path).path
        if route not in ("/", "/download", "/download/"):
            self.send_error(404, "Not found")
            return
        if not HTML_FILE.is_file():
            self.send_error(404, "Question bank HTML is missing")
            return

        size = HTML_FILE.stat().st_size
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Disposition", 'attachment; filename="CoreBTR-Qbank.html"')
        self.send_header("Content-Length", str(size))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            with HTML_FILE.open("rb") as stream:
                while chunk := stream.read(1024 * 1024):
                    self.wfile.write(chunk)
        except (BrokenPipeError, ConnectionResetError):
            # A client may cancel a large download; don't emit a noisy traceback.
            pass

    def log_message(self, fmt, *args):
        print(f"{self.address_string()} - {fmt % args}", flush=True)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", PORT), DownloadHandler)
    print(f"Download server listening on 0.0.0.0:{PORT}", flush=True)
    server.serve_forever()
