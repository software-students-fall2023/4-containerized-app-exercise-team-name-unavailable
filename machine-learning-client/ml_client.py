# Web stuff
from flask import Flask, request
from os import getenv

# AI stuff
import whisper
from torch import device

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
    # Unpickle audio data
    audio = pickle.loads(db_audio)
    model = whisper.load("tiny.en")
    model.device = device("cpu")


if __name__ == "__main__":
    main()
