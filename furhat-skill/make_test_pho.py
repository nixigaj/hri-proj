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


def wav_duration_s(path: Path) -> float:
    with contextlib.closing(wave.open(str(path), "r")) as f:
        return f.getnframes() / f.getframerate()


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


def make_pho(phonemes: list[str], total_s: float) -> dict:
    """Build Furhat iristk.speech.Transcription with even-spaced phones."""
    if not phonemes:
        return {"class": "iristk.speech.Transcription", "phones": []}
    dur = total_s / len(phonemes)
    phones = [
        {
            "class": "iristk.speech.Phone",
            "name": p,
            "start": round(i * dur, 3),
            "end": round((i + 1) * dur, 3),
        }
        for i, p in enumerate(phonemes)
    ]
    # Trailing silence so mouth closes
    phones.append({
        "class": "iristk.speech.Phone",
        "name": "_s",
        "start": phones[-1]["end"],
        "end": round(phones[-1]["end"] + 0.01, 3),
    })
    return {"class": "iristk.speech.Transcription", "phones": phones}


def main() -> None:
    if not WAV_PATH.exists():
        raise FileNotFoundError(f"{WAV_PATH} not found")

    duration_s = wav_duration_s(WAV_PATH)
    print(f"Audio duration: {duration_s:.2f} s")

    phonemes = get_phonemes(TRANSCRIPT)
    print(f"Phonemes ({len(phonemes)}): {' '.join(phonemes[:10])}...")

    pho = make_pho(phonemes, duration_s)
    PHO_PATH.write_text(json.dumps(pho, indent=2), encoding="utf-8")
    print(f"Written: {PHO_PATH}")
    print("\nTo test: start audio server and load sound_16k.wav in Furhat.")
    print("Furhat will look for sound_16k.pho at the same URL.")


if __name__ == "__main__":
    main()
