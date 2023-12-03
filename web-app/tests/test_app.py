import pytest
import app as web_app
from app import *
import base62
import mongomock

oidtob62 = lambda oid: base62.encodebytes(oid.binary)
b62tooid = lambda b62: ObjectId(base62.decodebytes(b62))


@pytest.fixture
def client(monkeypatch):
    # monkeypatch.setenv("FLASK_STAGE", "development")
    web_app.app.config["TESTING"] = True
    web_app.app.config["PRESERVE_CONTEXT_ON_EXCEPTION"] = False
    with web_app.app.test_client() as client:
        yield client


def test_login(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"<h1> Hello. Please sign in.</h1>" in response.data


def test_upload(client, monkeypatch):
    file = open("tests/test_audio.opus", "rb")
    # class MockFiles:
    #     def __init__(self):
    #         self.file_data = {}

    #     def __getitem__(self, key):
    #         return self.file_data[key]

    # mock_files = MockFiles()
    # mock_files.file_data["audio"] = type('MockedFile', (), {'read': lambda self: b'testdata'})

    def mock_post(*args, **kwargs):
        return "fakedata"

    def mock_pickle_dump():
        return "fakedata"

    def mock_insert_one(*args, **kwargs):
        return b62tooid("ejBdVtObtsZBmMr0")

    web_app.DB = mongomock.MongoClient().recordings

    # monkeypatch.setattr(web_app.pickle, "dumps", mock_pickle_dump)
    monkeypatch.setattr(requests, "post", mock_post)
    # monkeypatch.setattr(request,"files",mock_read)
    # monkeypatch.setattr(os,"read",mock_read())
    monkeypatch.setattr(web_app.DB.recordings, "insert_one", mock_insert_one)
    # monkeypatch.setattr(request.files,mock_files)
    # monkeypatch.delattr(request.files["audio"].read())
    # with web_app.app.test_request_context("/upload",method="POST", data={
    #         "audio" : "asdf",
    #         "name": "testName",
    #         "username": "testUsername"
    #     }):
    #     monkeypatch.setattr("app.request.files", mock_files)
    #     response = client.post(
    #     "/upload",
    #     data={
    #         "audio" : "asdf",
    #         "name": "testName",
    #         "username": "testUsername"
    #     }
    # )

    response = client.post(
        "/upload",
        data={"audio": file, "name": "testName", "username": "testUsername"},
    )

    # with client:
    #     response = client.post(
    #     "/upload",
    #     data={
    #         "audio" : "asdf",
    #         "name": "testName",
    #         "username": "testUsername"
    #     }
    # )
    assert response.status_code == 202

    file.close()


def test_record(client):
    response = client.get("/record")
    assert response.status_code == 200
    assert b"<h1>Make a Recording</h1>" in response.data


def test_get_audio_no_oid(client):
    response = client.get("/audio/")
    assert b"404 Not Found" in response.data


def test_get_audio_not_found(client, monkeypatch):
    web_app.DB = mongomock.MongoClient().recordings

    def mock_find_one(*args, **kwargs):
        return None

    monkeypatch.setattr(web_app.DB.recordings, "find_one", mock_find_one)
    response = client.get("/audio/ejBdVtObtsZBmMr0", follow_redirects=True)
    assert response.status_code == 404


def test_get_audio(client, monkeypatch):
    web_app.DB = mongomock.MongoClient().recordings
    exist_oid = "ejBdVtObtsZBmMr0"

    def mock_find_one(*args, **kwargs):
        if oidtob62(args[0]["_id"]) == exist_oid:
            return {"_id": args[0]["_id"],"audio":0}
        return None

    def mock_pickle_loads(*args, **kwargs):
        return b"fakedata"

    monkeypatch.setattr(web_app.DB.recordings, "find_one", mock_find_one)
    monkeypatch.setattr(web_app.pickle, "loads", mock_pickle_loads)
    response = client.get("/audio/ejBdVtObtsZBmMr0", follow_redirects=True)


def test_transcript_no_oid(client, monkeypatch):
    response = client.get("/transcript")
    assert response.status_code == 404


def test_transcript_404(client, monkeypatch):
    web_app.DB = mongomock.MongoClient().recordings

    def mock_find_one(*args, **kwargs):
        return None

    monkeypatch.setattr(web_app.DB.recordings, "find_one", mock_find_one)
    response = client.get("/transcript/ejBdVtObtsZBmMr0", follow_redirects=True)
    assert response.status_code == 404


def test_transscript(client, monkeypatch):
    web_app.DB = mongomock.MongoClient().recordings
    pass
