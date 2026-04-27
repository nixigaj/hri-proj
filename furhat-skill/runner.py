import time
from scenarios import SCENARIOS, audio_url


def run_scenario(
    scenario_id: int,
    voice: str,
    furhat,
    audio_base_url: str,
    input_fn=input,
    sleep_fn=time.sleep,
) -> None:
    scenario = SCENARIOS[scenario_id]
    menu_turns = scenario["menu_turns"]

    print(f"\nScenario {scenario_id}: {scenario['title']} | Voice: {voice}")
    print("─" * 50)

    for turn_id in scenario["turns"]:
        url = audio_url(audio_base_url, scenario_id, voice, turn_id)
        print(f"  [{turn_id}] Playing...")
        furhat.say(url=url, blocking=True)

        if turn_id in menu_turns:
            while True:
                cmd = input_fn("  > Enter=advance, r=repeat: ").strip().lower()
                if cmd == "r":
                    fx_url = audio_url(audio_base_url, scenario_id, voice, "FX")
                    furhat.say(url=fx_url, blocking=True)
                    furhat.say(url=url, blocking=True)
                else:
                    break
        else:
            sleep_fn(1.5)

    print("\n[Scenario complete]\n")
