# Web stuff
from flask import Flask, request
from os import getenv, remove

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
write_to_srt = lambda raw_transcription: (get_writer("srt", "."))(
    raw_transcription, **default_writer_args
)


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
    """Connects to database and launches Flask app"""
    global DB
    DB = MongoClient(
        "mongoDB://mongo:27017",
        username=getenv("MONGO_USER"),
        password=getenv("MONGO_PASSWORD"),
    )
    # TODO: Create the Flask app


@app.route("/transcribe", methods=["POST"])
def transcribe():
    """Takes object ID from request body and starts a transcription job"""
    # Get object ID from request
    oid = b62tooid(request.form["id"])
    # Get pickled opus audio data from database
    db_audio = DB.transcriptions_DB.transcriptions.find_one({"_id": oid})["audio"]
    # Write to .opus file
    with open(f"{request.form['id']}.opus", "wb") as f:
        f.write(pickle.loads(db_audio))
    model = whisper.load_model("tiny.en")
    model.device = device("cpu")
    # Transcribe audio into f"{request.form['id']}.srt" using transcribe() and get_writer()
    raw_transcription = whisper.transcribe(
        model,
        f"{request.form['id']}.opus",
    )
    write_to_srt(raw_transcription)
    # Put contents of f"{request.form['id']}.srt" into same document, and set finished to true
    with open(f"{request.form['id']}.srt", "r", encoding="utf-8") as f:
        DB.transcriptions_DB.transcriptions.update_one(
            {"_id": oid}, {"$set": {"transcript": f.read(), "finished": True}}
        )
    # Remove .opus and .srt files
    remove(f"{request.form['id']}.opus")
    remove(f"{request.form['id']}.srt")
    # Return 204 No Content
    return ("", 204)


if __name__ == "__main__":
    main()
