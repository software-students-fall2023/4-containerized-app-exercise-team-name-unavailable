import sys

# Web stuff
from flask import Flask, request
from os import getenv, remove
from gunicorn.app.base import BaseApplication
from multiprocessing import Process

# Note: Environment is provided in .env, but automatically loaded via docker compose.
# There is no need for load_dotenv().

app = Flask(__name__)

# AI stuff
import whisper
from whisper.utils import get_writer
from torch import device

# Obtained from whisper/transcribe.py (default CLI args)
default_writer_args = {
    "highlight_words": False,
    "max_line_count": None,
    "max_line_width": None,
    "max_words_per_line": None,
}


def write_to_srt(raw_transcription):
    """Takes output from whipser.transcribe() and writes it to an .srt file for later upload."""
    writer = get_writer("srt", ".")
    writer(raw_transcription, **default_writer_args)


# Database stuff
import base64
import base62
import pickle
from pymongo import MongoClient
from bson.objectid import ObjectId


oidtob62 = lambda oid: base64.encodebytes(oid.binary)
b62tooid = lambda b62: ObjectId(base62.decodebytes(b62))

DB = None


def main():
    """Connects to database and launches Flask app,
    under the assumption that this app is closed off from WAN."""
    global DB
    client = MongoClient(
        "mongoDB://mongo:27017",
        username=getenv("MONGO_USER"),
        password=getenv("MONGO_PASSWORD"),
    )
    DB = client["recordings"]
    try:
        assert getenv("FLASK_STAGE") in ["production", "development"]
    except AssertionError:
        print("FLASK_STAGE must be either 'production' or 'development'")
        sys.exit(1)
    if getenv("FLASK_STAGE") == "development":
        app.run(host="0.0.0.0", port=80, debug=True, load_dotenv=False)
    else:  # if production
        # Use gunicorn
        class FlaskApplication(BaseApplication):
            """Custom gunicorn application."""

            def __init__(self, application, options=None):
                self.options = options or {}
                self.application = application
                super().__init__()

            def init(self, parser, opts, args):
                """Unused init function."""
                pass

            def load_config(self):
                """Sets gunicorn config."""
                for key, value in self.options.items():
                    self.cfg.set(key, value)

            def load(self):
                """Returns the Flask application."""
                return self.application

        options = {
            "bind": "0.0.0.0:80",
            "workers": 1,
            "threads": 1,
            "worker_class": "sync",
        }

        FlaskApplication(app, options).run()


def transcribe_job(oid: ObjectId):
    """Takes base53 object ID and starts a transcription job asynchronously."""
    # Get pickled opus audio data from database
    db_audio = DB.recordings.find_one({"_id": oid})["audio"]
    filename = oidtob62(oid)
    # Write to .opus file
    with open(f"{filename}.opus", "wb") as f:
        f.write(pickle.loads(db_audio))
    model = whisper.load_model("tiny.en")
    model.device = device("cpu")
    # Transcribe audio into f"{filename}.srt" using transcribe() and get_writer()
    raw_transcription = whisper.transcribe(
        model,
        f"{filename}.opus",
    )
    write_to_srt(raw_transcription)
    # Put contents of f"{filename}.srt" into same document, and set finished to true
    with open(f"{filename}.srt", "r", encoding="utf-8") as f:
        DB.recordings.update_one(
            {"_id": oid}, {"$set": {"transcript": f.read(), "finished": True}}
        )
    # Remove .opus and .srt files
    remove(f"{filename}.opus")
    remove(f"{filename}.srt")


@app.route("/transcribe", methods=["POST"])
def transcribe():
    """Takes base53 object ID from request form and starts a transcription job."""
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
