"""Manual lipsync for virtual Furhat.

Virtual Furhat ignores .pho on URL audio. We replay the .pho timeline ourselves
by pushing request.face.params events over the realtime WebSocket while audio
plays via the Remote API.

Phoneme → JAW_OPEN amplitude is a coarse class-based mapping. Good enough to
read as speech; not visually perfect.
"""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path

import websocket  # from websocket-client


REALTIME_WS_URL = "ws://localhost:9000/v1/events"

# Coarse phoneme → jaw opening amplitude (0..1).
# Covers espeak (Kirshenbaum) and MFA-Swedish (IPA-ish) labels.
_OPEN_VOWELS = set("aAæɑɒɐ")
_MID_VOWELS = set("eEoOɛɔœøöäɘəɵ@2367")
_CLOSE_VOWELS = set("iIuUyYʉɪʊ")
_APPROX = set("lrRwjJʁɥɭɽ")
_BILABIAL_CLOSURE = set("mpbɱ")  # mouth shut


def _phoneme_amp(label: str) -> float:
    if not label or label in ("_s", "sil", "sp", "spn", ""):
        return 0.0
    head = label[0]
    if head in _BILABIAL_CLOSURE:
        return 0.05
    if head in _OPEN_VOWELS:
        return 0.7
    if head in _MID_VOWELS:
        return 0.45
    if head in _CLOSE_VOWELS:
        return 0.25
    if head in _APPROX:
        return 0.25
    return 0.2  # generic consonant


def load_pho(path: Path) -> list[tuple[float, float, str]]:
    """Return list of (start_s, end_s, phoneme_label) from a Furhat .pho file."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    phones = data.get("phones", []) if isinstance(data, dict) else data
    out = []
    for p in phones:
        name = p.get("name") or p.get("phoneme") or ""
        if "start" in p and "end" in p:
            start, end = float(p["start"]), float(p["end"])
        elif "start" in p and "duration" in p:
            start = float(p["start"]) / 1000.0
            end = start + float(p["duration"]) / 1000.0
        else:
            continue
        if end > start:
            out.append((start, end, name))
    return out


def _build_frames(phones: list[tuple[float, float, str]], fps: int = 50) -> list[tuple[float, float]]:
    """Sample the phoneme timeline at fixed fps → list of (t_seconds, jaw_open).

    Linear interpolation between phoneme midpoints gives a smoother mouth than
    step-stepping at phone boundaries.
    """
    if not phones:
        return []
    samples = [(0.5 * (s + e), _phoneme_amp(lbl)) for s, e, lbl in phones]
    total = phones[-1][1]
    frames = []
    dt = 1.0 / fps
    t = 0.0
    j = 0
    while t <= total + dt:
        # Advance j so samples[j] is the last point with time <= t (when possible)
        while j + 1 < len(samples) and samples[j + 1][0] <= t:
            j += 1
        if j + 1 < len(samples):
            t0, a0 = samples[j]
            t1, a1 = samples[j + 1]
            if t1 > t0:
                frac = max(0.0, min(1.0, (t - t0) / (t1 - t0)))
                amp = a0 + (a1 - a0) * frac
            else:
                amp = a1
        else:
            amp = samples[-1][1]
        frames.append((t, round(amp, 3)))
        t += dt
    # Force closed mouth at end
    frames.append((total + dt, 0.0))
    return frames


def _send_face_params(ws: websocket.WebSocket, jaw_open: float) -> None:
    ws.send(json.dumps({
        "type": "request.face.params",
        "params": {"JAW_OPEN": jaw_open},
    }))


class LipsyncPlayer:
    """Plays a .pho timeline against the Furhat realtime WebSocket in a thread."""

    def __init__(self, pho_path: Path, ws_url: str = REALTIME_WS_URL, fps: int = 50,
                 start_delay_s: float = 0.0):
        self.frames = _build_frames(load_pho(pho_path), fps=fps)
        self.ws_url = ws_url
        self.start_delay_s = start_delay_s
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()

    def start(self) -> None:
        if not self.frames:
            return
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def join(self, timeout: float | None = None) -> None:
        if self._thread:
            self._thread.join(timeout)

    def stop(self) -> None:
        self._stop.set()

    def _run(self) -> None:
        try:
            ws = websocket.create_connection(self.ws_url, timeout=5)
        except Exception as e:
            print(f"[lipsync] WS connect failed: {e}")
            return
        try:
            t0 = time.monotonic() + self.start_delay_s
            for t, amp in self.frames:
                if self._stop.is_set():
                    break
                target = t0 + t
                gap = target - time.monotonic()
                if gap > 0:
                    time.sleep(gap)
                try:
                    _send_face_params(ws, amp)
                except Exception:
                    break
            try:
                _send_face_params(ws, 0.0)
            except Exception:
                pass
        finally:
            try:
                ws.close()
            except Exception:
                pass
