import contextlib
import os
import time
import wave

from lipsync_driver import LipsyncPlayer
from scenarios import SCENARIOS, audio_url


def _wav_duration(path: str) -> float:
    with contextlib.closing(wave.open(path, "r")) as f:
        return f.getnframes() / f.getframerate()


def _say_blocking(furhat, url: str, wav_path: str, sleep_fn) -> None:
    """Play url; drive lipsync from .pho if present (virtual Furhat ignores lipsync flag)."""
    duration = _wav_duration(wav_path)
    pho_path = os.path.splitext(wav_path)[0] + ".pho"

    player = LipsyncPlayer(pho_path) if os.path.exists(pho_path) else None
    t0 = time.monotonic()
    furhat.say(url=url, lipsync=True, blocking=False)
    if player:
        player.start()
    gap = duration - (time.monotonic() - t0)
    if gap > 0:
        sleep_fn(gap)
    if player:
        player.join(timeout=1.0)


def run_scenario(
    scenario_id: int,
    voice: str,
    furhat,
    audio_base_url: str,
    audio_dir: str,
    input_fn=input,
    sleep_fn=time.sleep,
) -> None:
    scenario = SCENARIOS[scenario_id]
    menu_turns = scenario["menu_turns"]

    print(f"\nScenario {scenario_id}: {scenario['title']} | Voice: {voice}")
    print("─" * 50)

    furhat.attend(user="CLOSEST")

    session_cb = str(int(time.time()))

    for turn_id in scenario["turns"]:
        wav_path = os.path.join(audio_dir, f"S{scenario_id}", voice, f"{turn_id}.wav")
        url = audio_url(audio_base_url, scenario_id, voice, turn_id, cb=session_cb)
        print(f"  [{turn_id}] Playing...")
        furhat.gesture(name="Nod", blocking=False)
        _say_blocking(furhat, url, wav_path, sleep_fn)

        if turn_id in menu_turns:
            repeat_n = 0
            while True:
                cmd = input_fn("  > Enter=advance, r=repeat: ").strip().lower()
                if cmd == "r":
                    repeat_n += 1
                    repeat_cb = f"{session_cb}-{turn_id}-{repeat_n}"
                    fx_path = os.path.join(audio_dir, f"S{scenario_id}", voice, "FX.wav")
                    fx_url = audio_url(audio_base_url, scenario_id, voice, "FX", cb=repeat_cb)
                    repeat_url = audio_url(audio_base_url, scenario_id, voice, turn_id, cb=f"{repeat_cb}-r")
                    _say_blocking(furhat, fx_url, fx_path, sleep_fn)
                    _say_blocking(furhat, repeat_url, wav_path, sleep_fn)
                elif cmd == "":
                    break
                else:
                    print("  [Enter=advance, r=repeat]")
        else:
            sleep_fn(1.5)

    print("\n[Scenario complete]\n")
