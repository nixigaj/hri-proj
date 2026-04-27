import argparse
import os
import sys

from furhat_remote_api import FurhatRemoteAPI

from audio_server import start_audio_server
from runner import run_scenario
from scenarios import SCENARIOS


def parse_args():
    parser = argparse.ArgumentParser(description="Furhat HRI Study — W-o-Z Skill")
    parser.add_argument("--scenario", type=int, required=True, choices=[1, 2, 3],
                        help="Scenario number (1=Retur, 2=Orderfråga, 3=Reklamation)")
    parser.add_argument("--voice", type=str, required=True,
                        choices=["tts", "rikssvenska", "skånska"],
                        help="Voice condition")
    return parser.parse_args()


def preflight_check(scenario_id: int, voice: str, audio_dir: str) -> None:
    scenario = SCENARIOS[scenario_id]
    all_turns = scenario["turns"] + ["FX"]
    missing = []
    for turn_id in all_turns:
        path = os.path.join(audio_dir, f"S{scenario_id}", voice, f"{turn_id}.wav")
        if not os.path.exists(path):
            missing.append(path)
    if missing:
        print("Missing audio files:")
        for p in missing:
            print(f"  {p}")
        sys.exit(1)


def main():
    args = parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    audio_dir = os.path.join(script_dir, "audio")

    preflight_check(args.scenario, args.voice, audio_dir)

    audio_base_url = start_audio_server(audio_dir, port=8000)

    try:
        furhat = FurhatRemoteAPI("localhost")
        furhat.furhat_get()  # probe: raises if Launcher is not reachable
    except Exception as e:
        print(f"Could not connect to Furhat on localhost:54321: {e}")
        print("Start the Furhat Launcher before running this skill.")
        sys.exit(1)

    run_scenario(args.scenario, args.voice, furhat, audio_base_url)


if __name__ == "__main__":
    main()
