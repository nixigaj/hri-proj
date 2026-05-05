#!/usr/bin/env python3
"""Create a rough .pho file for sound_16k.wav to test Furhat lip-sync pipeline.

Phonemes are evenly distributed across the audio duration — not accurate,
but sufficient to verify that Furhat reads and uses .pho files at all.

Run from furhat-skill/:
    .venv/bin/python make_test_pho.py
"""

import json
import subprocess
import wave
import contextlib
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
WAV_PATH = SCRIPT_DIR / "audio" / "sound_16k.wav"
PHO_PATH = SCRIPT_DIR / "audio" / "sound_16k.pho"

TRANSCRIPT = (
    "The fitnessgram pacer test is a multi stage aerobic capacity test "
    "that progressively gets more difficult as it continues."
)


def wav_duration_ms(path: Path) -> float:
    with contextlib.closing(wave.open(str(path), "r")) as f:
        return f.getnframes() / f.getframerate() * 1000


def get_phonemes(text: str) -> list[str]:
    result = subprocess.run(
        ["espeak-ng", "-q", "-x", "--sep= ", text],
        capture_output=True, text=True,
    )
    raw = result.stdout.strip()
    # Split and filter empty / stress/boundary markers
    tokens = []
    for tok in raw.split():
        tok = tok.strip("',")
        if tok and not tok.startswith("_"):
            tokens.append(tok)
    return tokens


def make_pho(phonemes: list[str], total_ms: float) -> list[dict]:
    if not phonemes:
        return []
    dur = total_ms / len(phonemes)
    return [
        {"phoneme": p, "start": round(i * dur), "duration": round(dur)}
        for i, p in enumerate(phonemes)
    ]


def main() -> None:
    if not WAV_PATH.exists():
        raise FileNotFoundError(f"{WAV_PATH} not found")

    duration_ms = wav_duration_ms(WAV_PATH)
    print(f"Audio duration: {duration_ms:.0f} ms")

    phonemes = get_phonemes(TRANSCRIPT)
    print(f"Phonemes ({len(phonemes)}): {' '.join(phonemes[:10])}...")

    pho = make_pho(phonemes, duration_ms)
    PHO_PATH.write_text(json.dumps(pho, indent=2), encoding="utf-8")
    print(f"Written: {PHO_PATH}")
    print("\nTo test: start audio server and load sound_16k.wav in Furhat.")
    print("Furhat will look for sound_16k.pho at the same URL.")


if __name__ == "__main__":
    main()
