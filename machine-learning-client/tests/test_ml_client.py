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
        mock_mongo_client["recordings"].return_value = mock_mongo_client["recordings"]

        with patch("ml_client.app.run") as mock_app_run:
            main()

            mock_mongo_client.assert_called_once_with(
                "mongodb://test_user:test_password@mongo:27017/recordings"
            )

            def mock_list_database_names(*args, **kwargs):
                pass

            def mock_list_collection_names(*args, **kwargs):
                pass

            def mock_create_database(*args, **kwargs):
                pass

            def mock_create_collection(*args, **kwargs):
                pass

            monkeypatch.setattr(
                mock_mongo_client, "list_database_names", mock_list_database_names
            )
            monkeypatch.setattr(
                mock_mongo_client["recordings"],
                "list_collection_names",
                mock_list_collection_names,
            )
            monkeypatch.setattr(
                mock_mongo_client, "create_database", mock_create_database
            )
            monkeypatch.setattr(
                mock_mongo_client["recordings"],
                "create_collection",
                mock_create_collection,
            )

            mock_app_run.assert_called_once_with(
                host="0.0.0.0", port=80, debug=True, load_dotenv=False
            )
