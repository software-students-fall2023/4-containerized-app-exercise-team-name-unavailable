# Web stuff
from flask import Flask, request

app = Flask(__name__)

# Environment variables
from os import remove, environ
from dotenv import load_dotenv

# AI stuff
from multiprocessing import Process
import whisper
from whisper.utils import get_writer

# Obtained from whisper/transcribe.py (default CLI args)
default_writer_args = {
    "highlight_words": False,
    "max_line_count": None,
    "max_line_width": None,
    "max_words_per_line": None,
}


# def write_to_srt(raw_transcription):
#     """Takes output from whisper.transcribe() and writes it to an .srt file for later upload."""
#     writer = get_writer("srt", ".")
#     writer(raw_transcription, **default_writer_args)


# Database stuff
import base62
import pickle
from pymongo import MongoClient
from bson.objectid import ObjectId


oidtob62 = lambda oid: base62.encodebytes(oid.binary)
b62tooid = lambda b62: ObjectId(base62.decodebytes(b62).hex())

DB = None


def main():
    """Connects to database and launches Flask app,
    under the assumption that this app is closed off from WAN."""
    global DB
    assert load_dotenv(dotenv_path="/certs/.env", override=True)
    client = MongoClient(
        f"mongodb://{environ.get('MONGO_USERNAME')}:{environ.get('MONGO_PASSWORD')}@mongo"
    )
    DB = client["recordings"]
    app.run(host="0.0.0.0", port=80, load_dotenv=False)


def fetch(oid: ObjectId):
    """Loads audio data from database into oid_b62.webm, returns oid_b62."""
    # Get pickled opus audio data from database
    db_audio = DB.recordings.find_one({"_id": oid})["audio"]
    filename = oidtob62(oid)
    # Write to .webm file
    with open(f"{filename}.webm", "wb") as f:
        f.write(pickle.loads(db_audio))
    return filename


def unload(oid: ObjectId):
    """Removes audio data and transcript from filesystem after upload to DB."""
    filename = oidtob62(oid)
    remove(f"{filename}.webm")
    remove(f"{filename}.srt")


def transcribe_job(oid: ObjectId):
    """Takes base62 object ID and starts a transcription job asynchronously."""
    # Get pickled opus audio data from database
    filename = fetch(oid)
    model = whisper.load_model("tiny.en", device="cpu")
    # Transcribe audio into f"{filename}.srt" using transcribe() and get_writer()
    raw_transcription = whisper.transcribe(
        model,
        f"{filename}.webm",
    )
    writer = get_writer("srt", ".")
    writer(raw_transcription, audio_path=f"/{filename}.webm", **default_writer_args)
    # Put contents of f"{filename}.srt" into same document, and set finished to true
    with open(f"{filename}.srt", "r", encoding="utf-8") as f:
        DB.recordings.update_one(
            {"_id": oid}, {"$set": {"transcript": f.read(), "finished": True}}
        )
    unload(oid)


@app.route("/transcribe", methods=["POST"])
def transcribe():
    """Takes base62 object ID from request form and starts a transcription job."""
    # Get object ID from request
    oid = b62tooid(request.form["id"])
    # Check that database has object ID
    try:
        assert DB.recordings.find_one({"_id": oid}) is not None
    except AssertionError:
        return ("", 404)
    # Run the transcription job (note that the web app prevents duplicate requests)
    Process(target=transcribe_job, args=(oid,)).start()
    return ("", 202)


@app.route("/", methods=["GET"])
def index():
    """Confirms, externally, that the server is running."""
    return ("", 204)


if __name__ == "__main__":
    main()
