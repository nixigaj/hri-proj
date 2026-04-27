VALID_VOICES = {"tts", "rikssvenska", "skånska"}
VALID_SCENARIOS = {1, 2, 3}

SCENARIOS = {
    1: {
        "title": "Retur",
        "turns": ["F1", "F2", "F3", "F4", "F5", "F6"],
        "menu_turns": {"F1", "F2", "F3", "F5"},
    },
    2: {
        "title": "Orderfråga",
        "turns": ["F1", "F2", "F3", "F4", "F5", "F6"],
        "menu_turns": {"F1", "F2", "F3", "F5"},
    },
    3: {
        "title": "Reklamation",
        "turns": ["F1", "F2", "F3", "F4", "F5", "F6"],
        "menu_turns": {"F1", "F2", "F3", "F5"},
    },
}


def audio_url(base_url: str, scenario_id: int, voice: str, turn_id: str) -> str:
    return f"{base_url}/S{scenario_id}/{voice}/{turn_id}.wav"
