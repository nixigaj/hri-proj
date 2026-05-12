import functools
import http.server
import socket
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


def _detect_lan_ip(target: str = "8.8.8.8") -> str:
    """Return local source IP used to reach `target` (without sending packets)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((target, 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def start_audio_server(audio_dir: str, port: int = 8000, advertise_host: str | None = None,
                       reach_host: str | None = None) -> str:
    """Start server. Binds 0.0.0.0 so remote Furhat can reach it.

    advertise_host: host string to use in returned URL. If None or "localhost",
      use "localhost". If "auto", auto-detect source IP toward `reach_host`
      (so multi-iface hosts pick the correct interface, e.g. VPN tunnel).
      Otherwise used verbatim.
    reach_host: target IP for auto-detection (typically Furhat's host).
    """
    handler = functools.partial(_LoggingHandler, directory=audio_dir)
    server = http.server.HTTPServer(("0.0.0.0", port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    if advertise_host is None or advertise_host == "localhost":
        host = "localhost"
    elif advertise_host == "auto":
        host = _detect_lan_ip(reach_host) if reach_host else _detect_lan_ip()
    else:
        host = advertise_host
    return f"http://{host}:{port}"
