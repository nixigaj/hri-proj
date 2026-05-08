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
from lipsync_driver import LipsyncPlayer

SCRIPT_DIR = Path(__file__).parent
AUDIO_DIR = SCRIPT_DIR / "audio"


def main():
    if not (AUDIO_DIR / "sound_16k.wav").exists():
        sys.exit("sound_16k.wav not found in audio/")
    if not (AUDIO_DIR / "sound_16k.pho").exists():
        sys.exit("sound_16k.pho not found — run make_test_pho.py first")

    base_url = start_audio_server(str(AUDIO_DIR), port=8000)
    # Cache-bust so Furhat can't reuse a previous fetch
    import time as _t
    cb = int(_t.time())
    wav_url = f"{base_url}/sound_16k.wav?cb={cb}"
    print(f"Serving: {wav_url}")
    print(f"Furhat will fetch .pho from: {base_url}/sound_16k.pho?cb={cb}")

    try:
        furhat = FurhatRemoteAPI("localhost")
        furhat.furhat_get()
    except Exception as e:
        sys.exit(f"Cannot connect to Furhat: {e}")

    # Pick first available voice. Prefer Neural (emits visemes for lipsync);
    # *-generative voices have no speech marks.
    try:
        voices = furhat.get_voices()
        if not voices:
            sys.exit("No voices available on Furhat. Enable one in Launcher → Settings → Voices.")
        print(f"Available voices: {[v.name for v in voices[:10]]}")
        neural = [v for v in voices if "Neural" in v.name]
        chosen = (neural or voices)[0].name
        furhat.set_voice(name=chosen)
        print(f"Voice set: {chosen}")
    except SystemExit:
        raise
    except Exception as e:
        sys.exit(f"Voice selection failed: {e}")

    # Test 0: gesture — does anything move at all?
    print("\n[Test 0] Gesture — does anything move?")
    furhat.attend(user="CLOSEST")
    furhat.gesture(name="Smile", blocking=True)
    input("Did anything move? Press Enter...")

    # Test 1: TTS — lip sync should always work with text
    print("\n[Test 1] TTS lip sync — does the mouth move?")
    furhat.say(text="Hej, jag testar nu om munrörelserna fungerar.", blocking=True)
    input("Press Enter to continue to audio test...")

    # Test 2: URL audio + manual lipsync driver
    print("\n[Test 2] URL audio with manual lipsync driver — mouth should move with audio")
    player = LipsyncPlayer(AUDIO_DIR / "sound_16k.pho")
    furhat.say(url=wav_url, lipsync=True, blocking=False)
    player.start()
    player.join(timeout=15)
    print("Done.")


if __name__ == "__main__":
    main()
