#!/usr/bin/env python3
"""Generate Furhat .pho lip-sync files using Montreal Forced Aligner (MFA).

Run this AFTER real audio recordings are in place — placeholder wavs produce
garbage alignment. Run once per voice delivery from your teammate.

Setup (one-time):
    conda create -n mfa -c conda-forge montreal-forced-aligner python=3.10
    conda activate mfa
    mfa model download acoustic swedish_mfa
    mfa model download dictionary swedish_mfa

Usage (with mfa conda env active, from furhat-skill/):
    python generate_pho.py

Output: places {turn}.pho alongside each {turn}.wav in audio/S{n}/{voice}/.
Furhat picks up .pho files automatically from the same URL as the .wav.

IMPORTANT: Transcripts below must match what was actually recorded.
Numbers are written as Swedish words (ett, två, tre...) — adjust if
the recording uses a different spoken form.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).parent
AUDIO_DIR = SCRIPT_DIR / "audio"
VOICES = ["tts", "rikssvenska", "skanska"]

TRANSCRIPTS: dict[int, dict[str, str]] = {
    1: {
        "F1": "Hej och välkommen till kundtjänst. Vad kan jag hjälpa dig med idag? Du kan säga retur, orderfråga, eller annat ärende.",
        "F2": "Du vill göra en retur. Vad gäller returen, fel storlek eller fel produkt?",
        "F3": "Tack. Jag ser ditt senaste köp, ett par skor från order fyra åtta två sju. Stämmer det?",
        "F4": "Tack. Jag skickar nu en returetikett till din epost. Skorna ska returneras inom fjorton dagar och pengarna återbetalas inom fem bankdagar.",
        "F5": "Är det något mer jag kan hjälpa dig med?",
        "F6": "Tack för att du kontaktade oss. Ha en bra dag.",
        "FX": "Förlåt, jag uppfattade inte. Kan du upprepa?",
    },
    2: {
        "F1": "Hej och välkommen till kundtjänst. Vad kan jag hjälpa dig med idag? Du kan säga retur, orderfråga, eller annat ärende.",
        "F2": "Du vill ställa en fråga om din order. Vad gäller frågan, leveransstatus eller ändring av beställning?",
        "F3": "Tack. Jag ser ditt senaste köp, en bordslampa från order fem ett nio tre. Stämmer det?",
        "F4": "Tack. Ditt paket är försenat med två dagar och förväntas levereras på fredag. Som kompensation skickas en rabattkod på tio procent till din epost.",
        "F5": "Är det något mer jag kan hjälpa dig med?",
        "F6": "Tack för att du kontaktade oss. Ha en bra dag.",
        "FX": "Förlåt, jag uppfattade inte. Kan du upprepa?",
    },
    3: {
        "F1": "Hej och välkommen till kundtjänst. Vad kan jag hjälpa dig med idag? Du kan säga reklamation, orderfråga, eller annat ärende.",
        "F2": "Du vill göra en reklamation. Vad gäller reklamationen, defekt produkt eller fel artikel?",
        "F3": "Tack. Jag ser ditt senaste köp, en vattenkokare från order sex fyra sju ett. Stämmer det?",
        "F4": "Tack. Jag skickar nu en ny vattenkokare till dig samt en hämtetikett för den defekta produkten. Allt skickas till din epost.",
        "F5": "Är det något mer jag kan hjälpa dig med?",
        "F6": "Tack för att du kontaktade oss. Ha en bra dag.",
        "FX": "Förlåt, jag uppfattade inte. Kan du upprepa?",
    },
}


def check_mfa() -> None:
    if not shutil.which("mfa"):
        sys.exit("ERROR: mfa not found on PATH. Activate the mfa conda environment:\n  conda activate mfa")


def check_real_audio() -> None:
    """Warn if all files are identical (placeholder audio)."""
    sizes = set()
    for scenario_id in (1, 2, 3):
        for voice in VOICES:
            for turn in ("F1", "F2", "F3"):
                p = AUDIO_DIR / f"S{scenario_id}" / voice / f"{turn}.wav"
                if p.exists():
                    sizes.add(p.stat().st_size)
    if len(sizes) == 1:
        print("WARNING: all wav files are identical — looks like placeholder audio.")
        print("         Run this script only after real recordings are in place.")
        resp = input("Continue anyway? [y/N] ").strip().lower()
        if resp != "y":
            sys.exit("Aborted.")


def prepare_corpus(corpus_dir: Path) -> int:
    """Write wav+lab pairs for all voices. Returns count of prepared files."""
    count = 0
    for voice in VOICES:
        speaker_dir = corpus_dir / voice
        speaker_dir.mkdir(parents=True, exist_ok=True)
        for scenario_id, turns in TRANSCRIPTS.items():
            for turn_id, text in turns.items():
                src = AUDIO_DIR / f"S{scenario_id}" / voice / f"{turn_id}.wav"
                if not src.exists():
                    print(f"  [skip] missing {src}")
                    continue
                stem = f"S{scenario_id}_{turn_id}"
                shutil.copy(src, speaker_dir / f"{stem}.wav")
                (speaker_dir / f"{stem}.lab").write_text(text, encoding="utf-8")
                count += 1
    return count


def run_mfa(corpus_dir: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        "mfa", "align", "--clean",
        str(corpus_dir),
        "swedish_mfa",
        "swedish_mfa",
        str(output_dir),
    ]
    print("Running:", " ".join(cmd))
    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit(f"MFA exited with code {result.returncode}")


def parse_phones_tier(tg_text: str) -> list[dict]:
    """Extract phoneme intervals from TextGrid as Furhat iristk.speech.Phone records.

    Furhat .pho format: start/end in seconds, silence labelled "_s".
    """
    m = re.search(r'name = "phones".*?intervals: size = \d+(.*?)(?=item \[|\Z)', tg_text, re.DOTALL)
    if not m:
        raise ValueError("No 'phones' tier found in TextGrid")

    phones = []
    for interval in re.finditer(
        r'xmin = ([\d.]+)\s+xmax = ([\d.]+)\s+text = "([^"]*)"',
        m.group(1),
    ):
        xmin = float(interval.group(1))
        xmax = float(interval.group(2))
        if xmax <= xmin:
            continue
        label = interval.group(3).strip() or "_s"
        phones.append({
            "class": "iristk.speech.Phone",
            "name": label,
            "start": round(xmin, 3),
            "end": round(xmax, 3),
        })
    # Ensure trailing silence so mouth closes
    if phones and phones[-1]["name"] != "_s":
        phones.append({
            "class": "iristk.speech.Phone",
            "name": "_s",
            "start": phones[-1]["end"],
            "end": round(phones[-1]["end"] + 0.01, 3),
        })
    return phones


def convert_textgrids(output_dir: Path) -> None:
    """Convert all TextGrid files to .pho and place next to source wavs."""
    for voice in VOICES:
        tg_dir = output_dir / voice
        if not tg_dir.exists():
            print(f"  [warn] no TextGrid output for {voice}")
            continue
        for tg_path in sorted(tg_dir.glob("*.TextGrid")):
            parts = tg_path.stem.split("_", 1)  # S1_F1 → ["S1", "F1"]
            if len(parts) != 2:
                continue
            scenario_id = int(parts[0][1:])
            turn_id = parts[1]

            tg_text = tg_path.read_text(encoding="utf-8")
            try:
                phones = parse_phones_tier(tg_text)
            except ValueError as e:
                print(f"  [error] {tg_path.name}: {e}")
                continue

            transcription = {
                "class": "iristk.speech.Transcription",
                "phones": phones,
            }
            pho_path = AUDIO_DIR / f"S{scenario_id}" / voice / f"{turn_id}.pho"
            pho_path.write_text(json.dumps(transcription, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"  {pho_path.relative_to(SCRIPT_DIR)}  ({len(phones)} phonemes)")


def main() -> None:
    check_mfa()
    check_real_audio()

    with tempfile.TemporaryDirectory(prefix="mfa_corpus_") as corpus_str, \
         tempfile.TemporaryDirectory(prefix="mfa_output_") as output_str:

        corpus_dir = Path(corpus_str)
        output_dir = Path(output_str)

        print("\nPreparing corpus...")
        n = prepare_corpus(corpus_dir)
        print(f"  {n} wav+lab pairs written")

        print("\nAligning...")
        run_mfa(corpus_dir, output_dir)

        print("\nConverting TextGrid → .pho...")
        convert_textgrids(output_dir)

    print("\nDone.")


if __name__ == "__main__":
    main()
