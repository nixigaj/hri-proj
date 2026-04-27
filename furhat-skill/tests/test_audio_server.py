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
