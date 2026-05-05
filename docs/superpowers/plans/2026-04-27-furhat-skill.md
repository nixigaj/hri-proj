# Furhat Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Python W-o-Z skill that plays pre-recorded audio through virtual Furhat for 3 customer service scenarios, driven by experimenter keypresses.

**Architecture:** Two processes on same machine — Furhat Launcher (virtual robot, HTTP API on `localhost:8080`) and `skill.py`. `skill.py` starts a local HTTP server serving wav files, connects to Furhat via `furhat-remote-api`, runs experimenter-driven loop where Enter=advance and r+Enter=repeat with error audio.

**Tech Stack:** Python 3.9+, `furhat-remote-api`, `pytest`, `argparse`, `http.server` (stdlib)

> **Audio file count:** 3 scenarios × 3 voices × 7 files (F1–F6 + FX) = **63 wav files**. The teammate generating audio was initially told 54 — remind them the FX error line adds 9 more (one FX per scenario per voice).

---

## File Map

| File | Responsibility |
|------|----------------|
| `furhat-skill/skill.py` | CLI entry point, arg parsing, preflight check, orchestration |
| `furhat-skill/scenarios.py` | Scenario data + `audio_url()` helper — pure functions, no I/O |
| `furhat-skill/audio_server.py` | Start HTTP server thread serving `audio/` directory |
| `furhat-skill/runner.py` | W-o-Z loop — plays turns, handles experimenter input |
| `furhat-skill/requirements.txt` | `furhat-remote-api`, `pytest` |
| `furhat-skill/tests/test_scenarios.py` | Tests for scenario data + URL generation |
| `furhat-skill/tests/test_audio_server.py` | Tests HTTP server starts and serves files |
| `furhat-skill/tests/test_runner.py` | Tests W-o-Z loop via mocked furhat + stdin |
| `furhat-skill/tests/test_skill.py` | Tests preflight check |
| `furhat-skill/audio/` | Wav files (not in repo — add to `.gitignore`) |

---

## Task 1: Project Scaffold

**Files:**
- Create: `furhat-skill/requirements.txt`
- Create: `furhat-skill/tests/__init__.py`
- Create: `furhat-skill/.gitignore`

- [ ] **Step 1: Create project directory and requirements**

```
furhat-skill/
├── requirements.txt
├── .gitignore
├── audio/               ← wav files go here (not committed)
└── tests/
    └── __init__.py
```

`furhat-skill/requirements.txt`:
```
furhat-remote-api
pytest
```

`furhat-skill/.gitignore`:
```
audio/
__pycache__/
*.pyc
.pytest_cache/
```

- [ ] **Step 2: Install dependencies**

```bash
cd furhat-skill
pip install -r requirements.txt
```

Expected: installs `furhat-remote-api` and `pytest` with no errors.

- [ ] **Step 3: Verify Furhat Remote API audio URL parameter**

Open a Python REPL and inspect the `say` method signature:
```python
from furhat_remote_api import FurhatRemoteAPI
import inspect
print(inspect.signature(FurhatRemoteAPI.say))
```

Expected: signature includes `url` parameter. If not, note the correct parameter name and adjust `runner.py` in Task 4 accordingly.

> **Note:** The spec documents `furhat.say(url="...", blocking=True)`. If `url` is not a supported kwarg, check the furhat-remote-api docs for the correct method to play audio from a URL before continuing.

- [ ] **Step 4: Create empty `tests/__init__.py`**

```bash
touch furhat-skill/tests/__init__.py
```

- [ ] **Step 5: Commit scaffold**

```bash
cd furhat-skill
git add requirements.txt .gitignore tests/__init__.py
git commit -m "chore: scaffold furhat-skill project"
```

---

## Task 2: Scenario Data (`scenarios.py`)

**Files:**
- Create: `furhat-skill/scenarios.py`
- Create: `furhat-skill/tests/test_scenarios.py`

- [ ] **Step 1: Write failing tests**

`furhat-skill/tests/test_scenarios.py`:
```python
import pytest
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
    assert VALID_VOICES == {"tts", "rikssvenska", "skånska"}


def test_valid_scenarios_contains_all_three():
    assert VALID_SCENARIOS == {1, 2, 3}
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd furhat-skill
pytest tests/test_scenarios.py -v
```

Expected: `ModuleNotFoundError: No module named 'scenarios'`

- [ ] **Step 3: Implement `scenarios.py`**

`furhat-skill/scenarios.py`:
```python
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
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
pytest tests/test_scenarios.py -v
```

Expected: all 9 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add scenarios.py tests/test_scenarios.py
git commit -m "feat: add scenario data and audio_url helper"
```

---

## Task 3: Audio HTTP Server (`audio_server.py`)

**Files:**
- Create: `furhat-skill/audio_server.py`
- Create: `furhat-skill/tests/test_audio_server.py`

- [ ] **Step 1: Write failing tests**

`furhat-skill/tests/test_audio_server.py`:
```python
import os
import tempfile
import urllib.request
from audio_server import start_audio_server


def test_returns_base_url():
    with tempfile.TemporaryDirectory() as tmpdir:
        base_url = start_audio_server(tmpdir, port=18000)
        assert base_url == "http://localhost:18000"


def test_serves_file_from_directory():
    with tempfile.TemporaryDirectory() as tmpdir:
        wav_path = os.path.join(tmpdir, "test.wav")
        with open(wav_path, "wb") as f:
            f.write(b"RIFF\x00\x00\x00\x00")
        base_url = start_audio_server(tmpdir, port=18001)
        response = urllib.request.urlopen(f"{base_url}/test.wav")
        assert response.read() == b"RIFF\x00\x00\x00\x00"


def test_serves_file_in_subdirectory():
    with tempfile.TemporaryDirectory() as tmpdir:
        sub = os.path.join(tmpdir, "S1", "tts")
        os.makedirs(sub)
        wav_path = os.path.join(sub, "F1.wav")
        with open(wav_path, "wb") as f:
            f.write(b"WAVE")
        base_url = start_audio_server(tmpdir, port=18002)
        response = urllib.request.urlopen(f"{base_url}/S1/tts/F1.wav")
        assert response.read() == b"WAVE"
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_audio_server.py -v
```

Expected: `ModuleNotFoundError: No module named 'audio_server'`

- [ ] **Step 3: Implement `audio_server.py`**

`furhat-skill/audio_server.py`:
```python
import functools
import http.server
import threading


def start_audio_server(audio_dir: str, port: int = 8000) -> str:
    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler,
        directory=audio_dir,
    )
    server = http.server.HTTPServer(("localhost", port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return f"http://localhost:{port}"
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
pytest tests/test_audio_server.py -v
```

Expected: all 3 tests PASS.

> Note: tests use ports 18000–18002 to avoid conflicts with the real server on 8000.

- [ ] **Step 5: Commit**

```bash
git add audio_server.py tests/test_audio_server.py
git commit -m "feat: add audio HTTP server"
```

---

## Task 4: W-o-Z Runner (`runner.py`)

**Files:**
- Create: `furhat-skill/runner.py`
- Create: `furhat-skill/tests/test_runner.py`

- [ ] **Step 1: Write failing tests**

`furhat-skill/tests/test_runner.py`:
```python
from unittest.mock import Mock, call
from runner import run_scenario


BASE_URL = "http://localhost:8000"


def _make_inputs(*cmds):
    it = iter(cmds)
    return lambda _prompt: next(it)


def test_plays_all_six_turns_on_happy_path():
    mock_furhat = Mock()
    # 4 menu turns (F1, F2, F3, F5) each need one Enter press
    run_scenario(1, "tts", mock_furhat, BASE_URL,
                 input_fn=_make_inputs("", "", "", ""),
                 sleep_fn=lambda _: None)
    assert mock_furhat.say.call_count == 6


def test_correct_url_for_each_turn():
    mock_furhat = Mock()
    run_scenario(1, "rikssvenska", mock_furhat, BASE_URL,
                 input_fn=_make_inputs("", "", "", ""),
                 sleep_fn=lambda _: None)
    called_urls = [c.kwargs["url"] for c in mock_furhat.say.call_args_list]
    assert called_urls == [
        f"{BASE_URL}/S1/rikssvenska/F1.wav",
        f"{BASE_URL}/S1/rikssvenska/F2.wav",
        f"{BASE_URL}/S1/rikssvenska/F3.wav",
        f"{BASE_URL}/S1/rikssvenska/F4.wav",
        f"{BASE_URL}/S1/rikssvenska/F5.wav",
        f"{BASE_URL}/S1/rikssvenska/F6.wav",
    ]


def test_repeat_adds_fx_and_replays_turn():
    mock_furhat = Mock()
    # r on F1, then Enter for F1 retry, then Enter for F2, F3, F5
    run_scenario(1, "tts", mock_furhat, BASE_URL,
                 input_fn=_make_inputs("r", "", "", "", ""),
                 sleep_fn=lambda _: None)
    # Expected calls: F1, FX, F1, F2, F3, F4, F5, F6 = 8
    assert mock_furhat.say.call_count == 8


def test_fx_url_is_called_on_repeat():
    mock_furhat = Mock()
    run_scenario(1, "tts", mock_furhat, BASE_URL,
                 input_fn=_make_inputs("r", "", "", "", ""),
                 sleep_fn=lambda _: None)
    called_urls = [c.kwargs["url"] for c in mock_furhat.say.call_args_list]
    assert f"{BASE_URL}/S1/tts/FX.wav" in called_urls


def test_non_menu_turns_trigger_sleep_not_input():
    mock_furhat = Mock()
    sleep_calls = []
    run_scenario(1, "tts", mock_furhat, BASE_URL,
                 input_fn=_make_inputs("", "", "", ""),
                 sleep_fn=sleep_calls.append)
    # F4 and F6 are non-menu turns → 2 sleep calls
    assert len(sleep_calls) == 2
    assert all(s == 1.5 for s in sleep_calls)


def test_say_called_with_blocking_true():
    mock_furhat = Mock()
    run_scenario(1, "tts", mock_furhat, BASE_URL,
                 input_fn=_make_inputs("", "", "", ""),
                 sleep_fn=lambda _: None)
    for c in mock_furhat.say.call_args_list:
        assert c.kwargs.get("blocking") is True


def test_scenario_2_uses_correct_scenario_id_in_url():
    mock_furhat = Mock()
    run_scenario(2, "skånska", mock_furhat, BASE_URL,
                 input_fn=_make_inputs("", "", "", ""),
                 sleep_fn=lambda _: None)
    called_urls = [c.kwargs["url"] for c in mock_furhat.say.call_args_list]
    assert all("/S2/" in url for url in called_urls)
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_runner.py -v
```

Expected: `ModuleNotFoundError: No module named 'runner'`

- [ ] **Step 3: Implement `runner.py`**

`furhat-skill/runner.py`:
```python
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
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
pytest tests/test_runner.py -v
```

Expected: all 8 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add runner.py tests/test_runner.py
git commit -m "feat: add W-o-Z runner loop"
```

---

## Task 5: CLI Entry Point and Preflight (`skill.py`)

**Files:**
- Create: `furhat-skill/skill.py`
- Create: `furhat-skill/tests/test_skill.py`

- [ ] **Step 1: Write failing tests**

`furhat-skill/tests/test_skill.py`:
```python
import os
import tempfile
import pytest
from skill import preflight_check


def _create_audio_files(tmpdir, scenario_id, voice):
    turns = ["F1", "F2", "F3", "F4", "F5", "F6", "FX"]
    subdir = os.path.join(tmpdir, f"S{scenario_id}", voice)
    os.makedirs(subdir, exist_ok=True)
    for t in turns:
        open(os.path.join(subdir, f"{t}.wav"), "w").close()


def test_preflight_passes_when_all_files_present():
    with tempfile.TemporaryDirectory() as tmpdir:
        _create_audio_files(tmpdir, 1, "tts")
        preflight_check(1, "tts", tmpdir)  # must not raise or exit


def test_preflight_fails_when_audio_dir_empty(capsys):
    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(SystemExit) as exc_info:
            preflight_check(1, "tts", tmpdir)
        assert exc_info.value.code == 1


def test_preflight_reports_missing_files(capsys):
    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(SystemExit):
            preflight_check(2, "rikssvenska", tmpdir)
        captured = capsys.readouterr()
        assert "F1.wav" in captured.out


def test_preflight_fails_when_one_file_missing(capsys):
    with tempfile.TemporaryDirectory() as tmpdir:
        _create_audio_files(tmpdir, 3, "skånska")
        os.remove(os.path.join(tmpdir, "S3", "skånska", "FX.wav"))
        with pytest.raises(SystemExit):
            preflight_check(3, "skånska", tmpdir)
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_skill.py -v
```

Expected: `ModuleNotFoundError: No module named 'skill'`

- [ ] **Step 3: Implement `skill.py`**

`furhat-skill/skill.py`:
```python
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
    except Exception as e:
        print(f"Could not connect to Furhat on localhost:8080: {e}")
        print("Start the Furhat Launcher before running this skill.")
        sys.exit(1)

    run_scenario(args.scenario, args.voice, furhat, audio_base_url)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
pytest tests/test_skill.py -v
```

Expected: all 4 tests PASS.

- [ ] **Step 5: Run full test suite**

```bash
pytest tests/ -v
```

Expected: all 24 tests PASS, 0 failures.

- [ ] **Step 6: Commit**

```bash
git add skill.py tests/test_skill.py
git commit -m "feat: add CLI entry point and preflight audio check"
```

---

## Task 6: Manual End-to-End Verification

No automated test — requires running virtual Furhat.

- [ ] **Step 1: Place placeholder audio files for testing**

Create one real wav file and symlink or copy it to all 63 positions to verify routing without waiting for ElevenLabs assets:

```bash
cd furhat-skill
python3 - <<'EOF'
import os, shutil
voices = ["tts", "rikssvenska", "skånska"]
turns = ["F1","F2","F3","F4","F5","F6","FX"]
# create a minimal valid wav (44 bytes)
wav = (b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00'
       b'\x01\x00\x80>\x00\x00\x00}\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00')
for s in [1,2,3]:
    for v in voices:
        d = f"audio/S{s}/{v}"
        os.makedirs(d, exist_ok=True)
        for t in turns:
            with open(f"{d}/{t}.wav","wb") as f:
                f.write(wav)
print("Placeholder audio files created.")
EOF
```

- [ ] **Step 2: Start virtual Furhat Launcher**

Open Furhat Launcher application. Start the virtual robot. Confirm it is running on `localhost:8080`.

- [ ] **Step 3: Run the skill for scenario 1, voice tts**

```bash
cd furhat-skill
python skill.py --scenario 1 --voice tts
```

Expected terminal output:
```
Scenario 1: Retur | Voice: tts
──────────────────────────────────────────────────
  [F1] Playing...
  > Enter=advance, r=repeat:
```

- [ ] **Step 4: Verify Furhat plays audio and W-o-Z controls work**

Press Enter at each menu prompt. Verify:
- Furhat plays each turn's audio in order
- F4 and F6 auto-advance after 1.5s pause
- Terminal prints `[Scenario complete]` after F6

- [ ] **Step 5: Verify repeat behaviour**

Restart and type `r` + Enter at F1. Verify:
- Furhat plays FX error audio
- Furhat replays F1 audio
- Prompt appears again
- Enter advances normally

- [ ] **Step 6: Verify invalid flag rejection**

```bash
python skill.py --scenario 4 --voice tts
```

Expected: argparse error, exits immediately, Furhat never contacted.

- [ ] **Step 7: Verify missing file detection**

```bash
rm audio/S1/tts/F3.wav
python skill.py --scenario 1 --voice tts
```

Expected:
```
Missing audio files:
  /path/to/furhat-skill/audio/S1/tts/F3.wav
```
Exits before connecting to Furhat. Restore the file after testing.

- [ ] **Step 8: Final commit**

```bash
git add audio/.gitkeep  # keep audio/ dir tracked but empty
git commit -m "test: verified end-to-end W-o-Z flow with virtual Furhat"
```
