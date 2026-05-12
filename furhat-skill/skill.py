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
                        choices=["tts", "rikssvenska", "skanska"],
                        help="Voice condition")
    parser.add_argument("--furhat-host", type=str,
                        default=os.environ.get("FURHAT_HOST", "localhost"),
                        help="Furhat Remote API host (default: $FURHAT_HOST or localhost)")
    parser.add_argument("--audio-host", type=str,
                        default=os.environ.get("AUDIO_HOST"),
                        help="Host to advertise audio URLs as. Default: 'localhost' "
                             "if --furhat-host is localhost, else auto-detect LAN IP.")
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
    # Propagate so lipsync_driver picks the right WebSocket host.
    os.environ["FURHAT_HOST"] = args.furhat_host

    script_dir = os.path.dirname(os.path.abspath(__file__))
    audio_dir = os.path.join(script_dir, "audio")

    preflight_check(args.scenario, args.voice, audio_dir)

    if args.audio_host:
        advertise = args.audio_host
    else:
        advertise = "localhost" if args.furhat_host == "localhost" else "auto"
    audio_base_url = start_audio_server(audio_dir, port=8000,
                                        advertise_host=advertise,
                                        reach_host=args.furhat_host)
    print(f"[audio-server] serving at {audio_base_url}")

    try:
        furhat = FurhatRemoteAPI(args.furhat_host)
        furhat.furhat_get()  # probe: raises if Remote API not reachable (port 54321)
    except Exception as e:
        print(f"Could not connect to Furhat Launcher at {args.furhat_host}: {e}")
        print("Ensure the Furhat Launcher is running and the virtual robot is started.")
        sys.exit(1)

    run_scenario(args.scenario, args.voice, furhat, audio_base_url, audio_dir)


if __name__ == "__main__":
    main()
