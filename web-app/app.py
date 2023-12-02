from flask import Flask, Response, render_template, request, redirect

from os import getenv
from bson.objectid import ObjectId

import os
import base62
import pymongo
import datetime
import requests
import pickle

oidtob62 = lambda oid: base62.encodebytes(oid.binary)
b62tooid = lambda b62: ObjectId(base62.decodebytes(b62).hex())

template_dir = os.path.abspath("./templates")
static_dir = os.path.abspath("./static")
template_dir = os.path.abspath("./templates")
static_dir = os.path.abspath("./static")
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

DB = None


def main():
    """Launches public-facing user interface for dictation app."""
    # connect to database
    global DB
    client = pymongo.MongoClient(
        "mongodb://mongo:27017",
        username=getenv("MONGO_USER"),
        password=getenv("MONGO_PASSWORD"),
    )
    DB = client["recordings"]
    # app.run(host="0.0.0.0", port=443, ssl_context=("cert.pem", "key.pem"))
    app.run(host="0.0.0.0", port=443)


@app.route("/")
def login():
    """Returns login page."""
    return render_template("login.html")


@app.route("/upload", methods=["POST"])
def upload():
    """Takes Opus audio from request body and saves it in database,
    along with recording name `name` and username `username`"""
    # get audio from request body (multipart/form-data), pickle it
    audio = pickle.dumps(request.files["audio"].read())
    # get name and username from request body
    name = request.form["name"]
    username = request.form["username"]
    # save audio in database
    oid = DB["recordings"].insert_one(
        {
            "name": name,
            "username": username,
            "audio": audio,
            "finished": False,
            "created": datetime.datetime.utcnow(),
        }
    )
    requests.post(
        "http://ml:80/transcribe",
        data={"id": oidtob62(oid)},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=5,  # 5 seconds, should be good enough
    )
    return 202


@app.route("/record")
def record():
    """Returns recording page."""
    return render_template("record.html")


@app.route("/audio/<oid_b62>")
def get_audio(oid_b62):
    """Returns audio file for recording with id `oid_b62`."""
    oid = b62tooid(oid_b62)
    recording = DB["recordings"].find_one({"_id": oid})
    if recording is None:
        return redirect("/404")
    audio = pickle.loads(recording["audio"])
    # Set MIME type to audio/ogg and return audio
    return Response(audio, mimetype="audio/ogg")


@app.route("/transcript/<oid_b62>")
def transcript(oid_b62):
    """Returns transcript page for recording with id `oid_b62`."""
    oid = b62tooid(oid_b62)
    # Get everything from recording document except audio
    recording = DB["recordings"].find_one({"_id": oid}, {"audio": 0})
    if recording is None:
        return redirect("/404")
    recording["id"] = oid_b62
    # Format creation date
    recording["created"] = recording["created"].strftime("%A, %B %d %Y, %I:%M:%S %p")
    if not recording["finished"]:
        recording["transcript"] = "Transcription in progress..."
    return render_template("transcript.html", recording=recording)


if __name__ == "__main__":
    main()
