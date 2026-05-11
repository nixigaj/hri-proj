import functools
import http.server
import sys
import threading


class _LoggingHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        sys.stdout.write(f"[audio-server] {self.address_string()} - {format % args}\n")
        sys.stdout.flush()

    def end_headers(self) -> None:
        # Furhat caches audio aggressively by URL — force refetch on every request.
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()


def start_audio_server(audio_dir: str, port: int = 8000) -> str:
    handler = functools.partial(_LoggingHandler, directory=audio_dir)
    server = http.server.HTTPServer(("localhost", port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return f"http://localhost:{port}"
