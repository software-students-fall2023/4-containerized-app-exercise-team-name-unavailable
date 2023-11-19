# Web stuff
from flask import Flask, request
from os import getenv, remove

app = Flask(__name__)

# AI stuff
import whisper
from torch import device

# Obtained from whisper/transcribe.py (default CLI args)
default_writer_args = {
    "highlight_words": False,
    "max_line_count": None,
    "max_line_width": None,
    "max_words_per_line": None,
}
write_to_srt = lambda raw_transcription: whisper.get_writer("srt", ".").write(
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

global db


def main():
    db = MongoClient(
        "mongodb://mongo:27017",
        username=getenv("MONGO_USER"),
        password=getenv("MONGO_PASSWORD"),
    )
    # TODO: Create the Flask app


"""
Document specification:
recording={
  _id: <ObjectId>,
  username: <username, string>,
  name: <recording name, string>,
  audio: <opus audio, pickled bytes>,
  finished: <true if finished, false if not, boolean>,
  transcript: <text inside .srt transcript from OpenAI whisper, null if not finished>,
  created: <timestamp of creation, using datetime.datetime.utcnow()>
}
"""


@app.route("/transcribe", methods=["POST"])
def transcribe():
    # Get object ID from request
    oid = b62tooid(request.form["id"])
    # Get pickled opus audio data from database
    db_audio = db.transcriptions_db.transcriptions.find_one({"_id": oid})["audio"]
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
    with open(f"{request.form['id']}.srt", "r") as f:
        db.transcriptions_db.transcriptions.update_one(
            {"_id": oid}, {"$set": {"transcript": f.read(), "finished": True}}
        )
    # Remove .opus and .srt files
    remove(f"{request.form['id']}.opus")
    remove(f"{request.form['id']}.srt")
    # Return 204 No Content
    return ("", 204)


if __name__ == "__main__":
    main()
