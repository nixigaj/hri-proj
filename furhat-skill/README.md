# Furhat skill — Wizard-of-Oz customer service

Wizard-of-Oz skill for the HRI study on Swedish dialects. Plays pre-recorded Furhat speech from a local HTTP server, drives lip movement manually, and lets the experimenter step through the scenario from the keyboard.

Targets the **virtual Furhat only** (SDK 2.9.x). See `../Scenarios/README.md` for scripts and scenario logic.

## Requirements

- Furhat Launcher (Desktop SDK) running with the virtual robot started → Remote API on `localhost:54321`, Realtime API on `localhost:9000`.
- Python 3.10+ (developed against 3.14).
- To generate `.pho` files: Montreal Forced Aligner in a separate conda env (see `generate_pho.py`).

## Install

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Run

```bash
.venv/bin/python skill.py --scenario {1|2|3} --voice {tts|rikssvenska|skanska}
```

- `--scenario 1` Retur, `2` Orderfråga, `3` Reklamation.
- `--voice tts` uses Furhat's built-in TTS, `rikssvenska`/`skanska` play the ElevenLabs recordings.

At each menu turn (F1, F2, F3, F5):
- `Enter` → advance
- `r` → play `FX` ("Förlåt, jag uppfattade inte…") followed by a repeat of the current turn

Any other key is ignored with a reminder.

## Audio files

Expected layout (not auto-created):

```
audio/
  S1/{tts,rikssvenska,skanska}/{F1..F6,FX}.wav
  S2/...
  S3/...
```

WAV: 16-bit PCM mono 16 kHz. `skill.py` runs a preflight check and exits if any file is missing.

## Lip sync

The virtual Furhat **ignores** the `lipsync` flag on URL audio — it never fetches the sibling `.pho` and never animates the mouth on its own. We drive lip movement manually instead:

1. `lipsync_driver.LipsyncPlayer` reads the `.pho` timeline next to the wav.
2. Maps each phoneme → a `JAW_OPEN` amplitude (0–1), sampled at 50 fps.
3. Pushes `request.face.params { JAW_OPEN }` events over `ws://localhost:9000/v1/events` in parallel with audio playback.

For the TTS condition, the voice must emit Polly speech marks — `*-Neural` works, `*-generative` does not (silent mouth despite audible TTS).

## Generating .pho

`.pho` files are produced from wav + transcript via Montreal Forced Aligner:

```bash
conda create -n mfa -c conda-forge montreal-forced-aligner python=3.10
conda activate mfa
mfa model download acoustic swedish_mfa
mfa model download dictionary swedish_mfa
python generate_pho.py
```

Writes `{turn}.pho` next to each `{turn}.wav`. Transcripts live in `generate_pho.py` — update if the recordings deviate.

Quick pipeline test without real recordings: `make_test_pho.py` builds a rough `.pho` for `audio/sound_16k.wav` using espeak-ng.

## Files

| File | Role |
|------|------|
| `skill.py` | CLI entry, preflight, Furhat connection |
| `runner.py` | Scenario loop, W-o-Z controls, calls `_say_blocking` |
| `scenarios.py` | Scenario data + `audio_url` helper |
| `audio_server.py` | Local HTTP server Furhat fetches wavs from |
| `lipsync_driver.py` | `.pho` → `JAW_OPEN` events over the Realtime WS |
| `generate_pho.py` | MFA-based `.pho` generator for real recordings |
| `make_test_pho.py` | espeak-based rough `.pho` for pipeline testing |
| `test_lipsync.py` | Manual sanity test (gesture / TTS / URL audio + lip sync) |
| `tests/` | pytest suite for runner/scenarios/skill/audio_server |

## Tests

```bash
.venv/bin/python -m pytest tests/ -q
```
