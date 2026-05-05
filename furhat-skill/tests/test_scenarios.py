from scenarios import audio_url, SCENARIOS, VALID_VOICES, VALID_SCENARIOS


def test_audio_url_format():
    url = audio_url("http://localhost:8000", 2, "rikssvenska", "F3")
    assert url == "http://localhost:8000/S2/rikssvenska/F3.wav"


def test_audio_url_fx():
    url = audio_url("http://localhost:8000", 1, "tts", "FX")
    assert url == "http://localhost:8000/S1/tts/FX.wav"


def test_all_scenarios_present():
    for sid in [1, 2, 3]:
        assert sid in SCENARIOS


def test_all_scenarios_have_six_turns():
    for sid, scenario in SCENARIOS.items():
        assert len(scenario["turns"]) == 6, f"Scenario {sid}: expected 6 turns"


def test_turn_ids_are_f1_through_f6():
    for sid, scenario in SCENARIOS.items():
        assert scenario["turns"] == ["F1", "F2", "F3", "F4", "F5", "F6"]


def test_menu_turns_are_subset_of_turns():
    for sid, scenario in SCENARIOS.items():
        for mt in scenario["menu_turns"]:
            assert mt in scenario["turns"], f"Scenario {sid}: menu turn {mt} not in turns"


def test_f4_and_f6_are_not_menu_turns():
    for sid, scenario in SCENARIOS.items():
        assert "F4" not in scenario["menu_turns"], f"Scenario {sid}: F4 should not be a menu turn"
        assert "F6" not in scenario["menu_turns"], f"Scenario {sid}: F6 should not be a menu turn"


def test_valid_voices_contains_all_three():
    assert VALID_VOICES == {"tts", "rikssvenska", "skanska"}


def test_valid_scenarios_contains_all_three():
    assert VALID_SCENARIOS == {1, 2, 3}
