import pytest
import os
import ml_client
import mongomock

from ml_client import *


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("FLASK_STAGE", "development")
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_get_writer(monkeypatch):
    def mock_writer(format, path):
        def write_to_file(transcription, **kwargs):
            with open("test_output.srt", "w") as file:
                file.write(transcription)

        return write_to_file

    monkeypatch.setattr(whisper.utils, "get_writer", mock_writer)

@pytest.fixture
def patch_mongo(monkeypatch):
    db = mongomock.MongoClient()
    def fake_mongo():
        return db
    monkeypatch.setattr('ml_client.client', fake_mongo)


def test_write_to_srt(mock_get_writer, monkeypatch):

    #mock_default_writer_args = {
    #   "highlight_words": False,
    #    "max_line_count": None,
    #    "max_line_width": None,
    #    "max_words_per_line": None,
    #}

    #monkeypatch.setattr(ml_client, "default_writer_args", mock_default_writer_args)

    raw_transcript = "This is a test"

    write_to_srt(raw_transcript)

    with open("test_output.srt", "r") as file:
        content = file.read()
        assert content == raw_transcript

    os.remove("test_output.srt")



class MockMongoClient:
    def __init__(self, *args, **kwargs):
        pass

    def __getitem__(self, item):
        return {}  # You can customize this mock as needed

class MockFlaskApp:
    @staticmethod
    def run(**kwargs):
        pass

def test_main_function(monkeypatch):
    monkeypatch.setenv("MONGO_USER", "test_user")
    monkeypatch.setenv("MONGO_PASSWORD", "test_password")

    monkeypatch.setattr('ml_client.MongoClient', MockMongoClient)

    monkeypatch.setattr('ml_client.app.run', MockFlaskApp.run)

    main()


def test_transcribe_job():
    pass


def test_transcribe_202(client, monkeypatch):

    ml_client.DB = mongomock.MongoClient().recordings
    exist_oid = b62tooid("ejBdVtObtsZBmMr0")

    def mock_find_one(*args, **kwargs):
        if args[0]["_id"] == exist_oid:
            return {"_id": exist_oid}
        return None

    monkeypatch.setattr(ml_client.DB, "find_one", mock_find_one)

    response = client.post("/transcribe", data={"id": exist_oid})

    assert response.status_code == 202


# def test_transcribe_404(client, monkeypatch):
#     ml_client.DB = mongomock.MongoClient().recordings
#     non_existing_oid = "mock_non_existing_id"

#     def mock_find_one(*args, **kwargs):
#         return None
#     monkeypatch.setattr(DB.transcriptions_DB.transcriptions, "find_one", mock_find_one)

#     response = client.post("/transcribe", data={"id": non_existing_oid})

#     assert response.status_code == 404


def test_index(client):
    response = client.get("/")
    assert response.status_code == 204
    assert response.data == b""
