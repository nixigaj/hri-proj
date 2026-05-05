# Furhat Skill — Design Spec

**Date:** 2026-04-27
**Project:** HRI study — Swedish dialect perception in customer service robot
**Status:** Approved

---

## Context

Three customer service scenarios run on a virtual Furhat robot. Voice is the only manipulated variable (TTS / Rikssvenska / Skånska). Interaction is phone-menu style — Furhat plays pre-recorded audio, experimenter advances via keyboard (Wizard-of-Oz). Participant never interacts with the computer directly.

This spec covers the Python skill that drives Furhat through a single scenario session.

---

## Architecture

Two processes on the same machine:

1. **Furhat Launcher** (virtual Furhat) — started manually before each session. Listens on `localhost:1932` (default).
2. **`skill.py`** — Python script. Experimenter runs it with CLI flags. Handles W-o-Z loop, audio serving, and Furhat control.

```
Furhat Launcher  ←──── furhat-remote-api ────  skill.py
                                                    │
                                            http.server thread
                                            (serves audio/ on :8000)
```

---

## CLI

```bash
python skill.py --scenario 2 --voice rikssvenska
```

| Flag | Values | Required |
|------|--------|----------|
| `--scenario` | `1`, `2`, `3` | Yes |
| `--voice` | `tts`, `rikssvenska`, `skånska` | Yes |

Invalid flag values → clear error message and exit before connecting to Furhat.

---

## File Structure

```
furhat-skill/
├── skill.py            # entry point, W-o-Z loop
├── scenarios.py        # turn sequence data for all 3 scenarios
├── requirements.txt    # furhat-remote-api
└── audio/
    ├── S1/
    │   ├── tts/        F1.wav F2.wav F3.wav F4.wav F5.wav F6.wav FX.wav
    │   ├── rikssvenska/ (same files)
    │   └── skånska/    (same files)
    ├── S2/ (same structure)
    └── S3/ (same structure)
```

**Total audio files:** 3 scenarios × 3 voices × 7 files (F1–F6 + FX) = **63 wav files**

Audio file naming is case-sensitive and must match folder names exactly:
- Voices: `tts`, `rikssvenska`, `skånska`
- Turns: `F1`, `F2`, `F3`, `F4`, `F5`, `F6`, `FX`

---

## Audio Serving

`skill.py` starts a `http.server.HTTPServer` thread on `localhost:8000` serving the `audio/` directory before connecting to Furhat. Furhat receives audio as:

```
http://localhost:8000/S2/rikssvenska/F3.wav
```

Thread is daemon — terminates automatically when main process exits.

---

## Scenario Data (`scenarios.py`)

```python
SCENARIOS = {
    1: {
        "title": "Retur",
        "turns": ["F1", "F2", "F3", "F4", "F5", "F6"],
        "menu_turns": ["F1", "F2", "F3", "F5"],   # turns that have a menu (Enter required)
    },
    2: {
        "title": "Orderfråga",
        "turns": ["F1", "F2", "F3", "F4", "F5", "F6"],
        "menu_turns": ["F1", "F2", "F3", "F5"],
    },
    3: {
        "title": "Reklamation",
        "turns": ["F1", "F2", "F3", "F4", "F5", "F6"],
        "menu_turns": ["F1", "F2", "F3", "F5"],
    },
}
```

`menu_turns` identifies turns where experimenter input is expected. Non-menu turns (F4, F6) play automatically with a short pause before advancing.

---

## W-o-Z Loop

For each turn in sequence:

1. Print turn ID and name to terminal: `[F2 — Undermeny] Playing…`
2. Send audio URL to Furhat (`furhat.say(url=..., blocking=True)`)
3. If turn is a **menu turn**: wait for experimenter input
   - **Enter** → advance to next turn
   - **`r` + Enter** → play `FX.wav` (error line), replay current turn audio, wait again
4. If turn is **non-menu** (F4, F6): short pause (`time.sleep(1.5)`), auto-advance
5. After F6: print `[Scenario complete]`, exit cleanly

---

## Error Handling

| Situation | Behaviour |
|-----------|-----------|
| Invalid `--scenario` or `--voice` flag | Print usage, exit before Furhat connect |
| Audio file missing | Print path, exit with clear message |
| Furhat not running / connection refused | Print connection error, exit |
| Experimenter sends unknown command | Print `[Enter=advance, r=repeat]`, wait again |

---

## Furhat Configuration

- Connect to `localhost:1932` (default virtual Furhat port)
- No ASR, no TTS — audio playback only
- Furhat face/persona: default virtual Furhat appearance (not customised in this skill)

> **Implementation note:** Verify the exact `furhat-remote-api` method for playing audio from a URL before writing code. Expected: `furhat.say(url="http://...", blocking=True)` — confirm against current SDK docs as the API has changed between versions.

---

## Out of Scope

- Questionnaire display or collection
- Latin square assignment (handled by experimenter guide, separate document)
- Audio file generation (ElevenLabs / TTS — separate task)
- Furhat Launcher configuration
