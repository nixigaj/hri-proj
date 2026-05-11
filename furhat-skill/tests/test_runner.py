from unittest.mock import Mock, patch
from runner import run_scenario

BASE_URL = "http://localhost:8000"
AUDIO_DIR = "/fake/audio"


def _make_inputs(*cmds):
    it = iter(cmds)
    return lambda _prompt: next(it)


@patch("runner._wav_duration", return_value=0.0)
def test_plays_all_six_turns_on_happy_path(mock_dur):
    mock_furhat = Mock()
    # 4 menu turns (F1, F2, F3, F5) each need one Enter press
    run_scenario(1, "tts", mock_furhat, BASE_URL, AUDIO_DIR,
                 input_fn=_make_inputs("", "", "", ""),
                 sleep_fn=lambda _: None)
    assert mock_furhat.say.call_count == 6


@patch("runner._wav_duration", return_value=0.0)
def test_correct_url_for_each_turn(mock_dur):
    mock_furhat = Mock()
    run_scenario(1, "rikssvenska", mock_furhat, BASE_URL, AUDIO_DIR,
                 input_fn=_make_inputs("", "", "", ""),
                 sleep_fn=lambda _: None)
    called_urls = [c.kwargs["url"].split("?")[0] for c in mock_furhat.say.call_args_list]
    assert called_urls == [
        f"{BASE_URL}/S1/rikssvenska/F1.wav",
        f"{BASE_URL}/S1/rikssvenska/F2.wav",
        f"{BASE_URL}/S1/rikssvenska/F3.wav",
        f"{BASE_URL}/S1/rikssvenska/F4.wav",
        f"{BASE_URL}/S1/rikssvenska/F5.wav",
        f"{BASE_URL}/S1/rikssvenska/F6.wav",
    ]


@patch("runner._wav_duration", return_value=0.0)
def test_repeat_adds_fx_and_replays_turn(mock_dur):
    mock_furhat = Mock()
    # r on F1, then Enter for F1 retry, then Enter for F2, F3, F5
    run_scenario(1, "tts", mock_furhat, BASE_URL, AUDIO_DIR,
                 input_fn=_make_inputs("r", "", "", "", ""),
                 sleep_fn=lambda _: None)
    # Expected calls: F1, FX, F1, F2, F3, F4, F5, F6 = 8
    assert mock_furhat.say.call_count == 8


@patch("runner._wav_duration", return_value=0.0)
def test_fx_url_is_called_on_repeat(mock_dur):
    mock_furhat = Mock()
    run_scenario(1, "tts", mock_furhat, BASE_URL, AUDIO_DIR,
                 input_fn=_make_inputs("r", "", "", "", ""),
                 sleep_fn=lambda _: None)
    called_urls = [c.kwargs["url"].split("?")[0] for c in mock_furhat.say.call_args_list]
    assert f"{BASE_URL}/S1/tts/FX.wav" in called_urls


@patch("runner._wav_duration", return_value=0.0)
def test_non_menu_turns_trigger_sleep_not_input(mock_dur):
    mock_furhat = Mock()
    sleep_calls = []
    run_scenario(1, "tts", mock_furhat, BASE_URL, AUDIO_DIR,
                 input_fn=_make_inputs("", "", "", ""),
                 sleep_fn=sleep_calls.append)
    # F4 and F6 are non-menu turns → 2 sleep calls of 1.5 s each
    assert len(sleep_calls) == 2
    assert all(s == 1.5 for s in sleep_calls)


@patch("runner._wav_duration", return_value=0.0)
def test_say_called_non_blocking_with_lipsync(mock_dur):
    """We drive timing+lipsync ourselves, so say() must not block."""
    mock_furhat = Mock()
    run_scenario(1, "tts", mock_furhat, BASE_URL, AUDIO_DIR,
                 input_fn=_make_inputs("", "", "", ""),
                 sleep_fn=lambda _: None)
    for c in mock_furhat.say.call_args_list:
        assert c.kwargs.get("blocking") is False
        assert c.kwargs.get("lipsync") is True


@patch("runner._wav_duration", return_value=0.0)
def test_scenario_2_uses_correct_scenario_id_in_url(mock_dur):
    mock_furhat = Mock()
    run_scenario(2, "skanska", mock_furhat, BASE_URL, AUDIO_DIR,
                 input_fn=_make_inputs("", "", "", ""),
                 sleep_fn=lambda _: None)
    called_urls = [c.kwargs["url"] for c in mock_furhat.say.call_args_list]
    assert all("/S2/" in url for url in called_urls)


@patch("runner._wav_duration", return_value=0.0)
def test_unknown_command_does_not_advance(mock_dur):
    mock_furhat = Mock()
    # junk input on F1, then Enter — should not advance on junk
    run_scenario(1, "tts", mock_furhat, BASE_URL, AUDIO_DIR,
                 input_fn=_make_inputs("junk", "", "", "", ""),
                 sleep_fn=lambda _: None)
    # F1 played once (no replay), junk ignored, then Enter advances
    # Total: F1-F6 = 6 calls (no FX, no replay)
    assert mock_furhat.say.call_count == 6
