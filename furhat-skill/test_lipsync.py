#!/usr/bin/env python3
"""Test Furhat lip-sync using sound_16k.wav + sound_16k.pho.

Run (with Furhat Launcher running):
    .venv/bin/python test_lipsync.py
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from audio_server import start_audio_server
from furhat_remote_api import FurhatRemoteAPI

SCRIPT_DIR = Path(__file__).parent
AUDIO_DIR = SCRIPT_DIR / "audio"


def main():
    if not (AUDIO_DIR / "sound_16k.wav").exists():
        sys.exit("sound_16k.wav not found in audio/")
    if not (AUDIO_DIR / "sound_16k.pho").exists():
        sys.exit("sound_16k.pho not found — run make_test_pho.py first")

    base_url = start_audio_server(str(AUDIO_DIR), port=8000)
    wav_url = f"{base_url}/sound_16k.wav"
    print(f"Serving: {wav_url}")
    print(f"Furhat will fetch .pho from: {base_url}/sound_16k.pho")

    try:
        furhat = FurhatRemoteAPI("localhost")
        furhat.furhat_get()
    except Exception as e:
        sys.exit(f"Cannot connect to Furhat: {e}")

    # Print what face/voices are available
    try:
        voices = furhat.get_voices()
        print(f"Available voices: {[v.name for v in voices[:5]]}")
    except Exception as e:
        print(f"Could not get voices: {e}")

    # Test 0: gesture — does anything move at all?
    print("\n[Test 0] Gesture — does anything move?")
    furhat.attend(user="CLOSEST")
    furhat.gesture(name="Smile", blocking=True)
    input("Did anything move? Press Enter...")

    # Test 1: TTS — lip sync should always work with text
    print("\n[Test 1] TTS lip sync — does the mouth move?")
    furhat.say(text="Hej, jag testar nu om munrörelserna fungerar.", blocking=True)
    input("Press Enter to continue to audio test...")

    # Test 2: URL audio — check server log below for .pho fetch
    print("\n[Test 2] Audio URL lip sync — watch server log for .pho request")
    furhat.say(url=wav_url, blocking=True)
    print("Done. Check above: did the server log show a GET for sound_16k.pho?")


if __name__ == "__main__":
    main()
