import pytest

from ml_client import *

@pytest.fixture
def client ( monkeypatch ):
    monkeypatch.setenv ( 'FLASK_STAGE', 'development' )
    app.config ['TESTING'] = True
    with app.test_client ( ) as client:
        yield client

def test_write_to_srt ( ):
    pass

def test_main ( ):
    pass

def test_transcribe_job ( ):
    pass

def test_transcribe ( ):
    pass

def test_index ( client ):
    response = client.get ( '/' )
    assert response.status_code == 204
    assert response.data == b''