import pytest
import os

from ml_client import *


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("FLASK_STAGE", "development")
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def mock_get_writer(monkeypatch):
    def mock_writer(format, path):
        def write_to_file(transcription, **kwargs):
            with open("test_output.srt", "w") as file:
                file.write(transcription)

        return write_to_file

    monkeypatch.setattr(whisper.utils, "get_writer", mock_writer)


def test_write_to_srt(mock_get_writer):
    raw_transcript = "This is a test"

    write_to_srt(raw_transcript)

    with open("test_output.srt", "r") as file:
        content = file.read()
        assert content == raw_transcript

    os.remove("test_output.srt")


def test_main():
    pass


def test_transcribe_job():
    pass


def test_transcribe_202(client, monkeypatch):
    exist_oid = "mock_existing_id"

    def mock_find_one(*args, **kwargs):
        if args[0]["_id"] == exist_oid:
            return {"_id": exist_oid}
        return None

    monkeypatch.setattr(DB.transcriptions_DB.transcriptions, "find_one", mock_find_one)

    response = client.post("/transcribe", data={"id": exist_oid})

    assert response.status_code == 202


def test_transcribe_404(client, monkeypatch):
    non_existing_oid = "mock_non_existing_id"

    def mock_find_one(*args, **kwargs):
        return None

    monkeypatch.setattr(DB.transcriptions_DB.transcriptions, "find_one", mock_find_one)

    response = client.post("/transcribe", data={"id": non_existing_oid})

    assert response.status_code == 404


def test_index(client):
    response = client.get("/")
    assert response.status_code == 204
    assert response.data == b""
