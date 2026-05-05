import os
import tempfile
import pytest
from skill import preflight_check


def _create_audio_files(tmpdir, scenario_id, voice):
    turns = ["F1", "F2", "F3", "F4", "F5", "F6", "FX"]
    subdir = os.path.join(tmpdir, f"S{scenario_id}", voice)
    os.makedirs(subdir, exist_ok=True)
    for t in turns:
        with open(os.path.join(subdir, f"{t}.wav"), "w"):
            pass


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
        _create_audio_files(tmpdir, 3, "skanska")
        os.remove(os.path.join(tmpdir, "S3", "skanska", "FX.wav"))
        with pytest.raises(SystemExit):
            preflight_check(3, "skanska", tmpdir)
