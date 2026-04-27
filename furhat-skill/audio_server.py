import functools
import http.server
import threading


def start_audio_server(audio_dir: str, port: int = 8000) -> str:
    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler,
        directory=audio_dir,
    )
    server = http.server.HTTPServer(("localhost", port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return f"http://localhost:{port}"
