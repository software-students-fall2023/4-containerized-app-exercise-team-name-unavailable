import pytest
import os
import ml_client
import mongomock
from unittest.mock import patch

from ml_client import *
from flask import Flask


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("FLASK_STAGE", "development")
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# @pytest.fixture
# def mock_get_writer(monkeypatch):
#     def mock_writer(format, path):
#         def write_to_file(transcription, **kwargs):
#             with open("test_output.srt", "w") as file:
#                 file.write(transcription)

#         return write_to_file

#     monkeypatch.setattr(whisper.utils, "get_writer", mock_writer)


# @pytest.fixture
# def patch_mongo(monkeypatch):
#     db = mongomock.MongoClient()

#     def fake_mongo():
#         return db

#     monkeypatch.setattr("ml_client.client", fake_mongo)


# class MockMongoClient:
#     def __init__(self, *args, **kwargs):
#         pass

#     def __getitem__(self, item):
#         return {}


# class MockFlaskApp:
#     @staticmethod
#     def run(**kwargs):
#         pass


# def test_transcribe_job(client, monkeypatch):
#     ml_client.DB = mongomock.MongoClient().recordings
#     non_exist_oid = "ejBdVtObtsZBmMr0"

#     def mock_find_one(*args, **kwargs):
#         if oidtob62(args[0]["_id"]) == non_exist_oid:
#             return {"_id": args[0]["_id"]}
#         return None

#     monkeypatch.setattr(ml_client.DB.recordings,"find_one",mock_find_one)
#     pass


# @pytest.fixture
# def sample_opus_data():
#     return b"Sample Opus Data"


# def test_transcribe_job(monkeypatch, sample_opus_data):
#     ml_client.DB = mongomock.MongoClient().recordings

#     def mock_find_one(*args, **kwargs):
#         return {"audio": sample_opus_data}

#     def mock_update_one(*args, **kwargs):
#         pass

#     monkeypatch.setattr("ml_client.DB.recordings.find_one", mock_find_one)
#     monkeypatch.setattr("ml_client.DB.recordings.update_one", mock_update_one)

#     monkeypatch.setattr("ml_client.whisper.load_model", lambda model: None)
#     monkeypatch.setattr(
#         "ml_client.whisper.transcribe", lambda model, filename: "Sample transcription"
#     )
#     monkeypatch.setattr(
#         "whisper.utils.get_writer", lambda *args, **kwargs: lambda x, y: None
#     )

#     oid = ObjectId("607be406d3a5b5a0b1e37c06")
#     transcribe_job(oid)

# def test_transcribe_job(client, monkeypatch):

#     ml_client.DB = mongomock.MongoClient().recordings
#     exist_oid = "ejBdVtObtsZBmMr0"

#     def mock_find_one(*args, **kwargs):
#         if oidtob62(args[0]["_id"]) == exist_oid:
#             return {"_id": args[0]["_id"]}

#     def mock_oidtob62(*args, **kwargs):
#         return "ejBdVtObtsZBmMr0"

#     def mock_whisper_load_model(*args, **kwargs):
#         return None

#     monkeypatch.setattr(ml_client.DB.recordings,"find_one", mock_find_one)
#     monkeypatch.setattr(ml_client, "oidtob62", mock_oidtob62)


def test_transcribe_202(client, monkeypatch):
    ml_client.DB = mongomock.MongoClient().recordings
    exist_oid = "ejBdVtObtsZBmMr0"

    def mock_find_one(*args, **kwargs):
        if oidtob62(args[0]["_id"]) == exist_oid:
            return {"_id": args[0]["_id"]}
        return None

    monkeypatch.setattr(ml_client.DB.recordings, "find_one", mock_find_one)
    response = client.post("/transcribe", data={"id": exist_oid})

    assert response.status_code == 202


def test_fetch(monkeypatch):
    """Check that fetch() makes a file with the correct name, immediately after it is called"""
    ml_client.DB = mongomock.MongoClient().recordings
    exist_oid = "ejBdVtObtsZBmMr0"

    def mock_find_one(*args):
        if oidtob62(args[0]["_id"]) == exist_oid:
            return {"_id": args[0]["_id"], "audio": b"Sample Opus Data"}
        return None

    def mock_pickle_loads(*args):
        return b"Fake Depickled Data"

    monkeypatch.setattr(ml_client.DB.recordings, "find_one", mock_find_one)
    monkeypatch.setattr(pickle, "loads", mock_pickle_loads)
    fetch(b62tooid(exist_oid))
    assert os.path.isfile(f"{exist_oid}.opus")
    os.remove(f"{exist_oid}.opus")


def test_unload(client, monkeypatch):
    """Check that unload() removes the files it is supposed to remove"""
    exist_oid = "ejBdVtObtsZBmMr0"
    open(f"{exist_oid}.opus", "w+", encoding="utf-8").close()
    open(f"{exist_oid}.srt", "w+", encoding="utf-8").close()
    unload(b62tooid(exist_oid))
    assert not os.path.isfile(f"{exist_oid}.opus")
    assert not os.path.isfile(f"{exist_oid}.srt")


def test_transcribe_404(client, monkeypatch):
    ml_client.DB = mongomock.MongoClient().recordings
    non_exist_oid = "ejBdVtObtsZBmMr0"

    def mock_find_one(*args, **kwargs):
        return None

    monkeypatch.setattr(ml_client.DB.recordings, "find_one", mock_find_one)

    response = client.post("/transcribe", data={"id": non_exist_oid})

    assert response.status_code == 404


def test_index(client):
    response = client.get("/")
    assert response.status_code == 204
    assert response.data == b""


def test_main(monkeypatch):
    monkeypatch.setenv("MONGO_USER", "test_user")
    monkeypatch.setenv("MONGO_PASSWORD", "test_password")

    with patch("ml_client.MongoClient") as mock_mongo_client:
        mock_mongo_client.return_value = mock_mongo_client
        mock_mongo_client.__getitem__.return_value = None

        with patch("ml_client.app.run") as mock_app_run:
            ml_client.main()

            mock_mongo_client.assert_called_once_with(
                "mongoDB://mongo:27017", username="test_user", password="test_password"
            )

            mock_mongo_client.__getitem__.assert_called_once_with("recordings")

            mock_app_run.assert_called_once_with(
                host="0.0.0.0", port=80, debug=True, load_dotenv=False
            )
