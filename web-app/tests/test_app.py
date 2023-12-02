import pytest
import app
from app import *
import base64

oidtob62 = lambda oid: base64.encodebytes(oid.binary)
b62tooid = lambda b62: ObjectId(base64.decodebytes(b62))

@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("FLASK_STAGE", "development")
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_login (client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"<h1> Hello. Please sign in.</h1>" in response.data

def test_upload():
    pass

# def test_record(client):
#     response = client.get("/record")
#     assert response == 200
#     assert b"<h1>Make a Recording</h1>" in response.data

def test_get_audio_404(client):
    response = client.get ("/audio/")
    assert b"404 Not Found" in response.data

def test_get_audio(client):
    pass