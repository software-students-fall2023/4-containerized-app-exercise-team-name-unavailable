from flask import Flask, Response, render_template, request, redirect, send_file

from os import getenv, path
from dotenv import load_dotenv

# .env stored in /certs
load_dotenv(dotenv_path="/certs/.env", override=True)

from bson.objectid import ObjectId

import base62
from pymongo import MongoClient, DESCENDING
import datetime
import requests
import pickle

oidtob62 = lambda oid: base62.encodebytes(oid.binary)
b62tooid = lambda b62: ObjectId(base62.decodebytes(b62).hex())

template_dir = path.abspath("./templates")
static_dir = path.abspath("./static")
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

DB = None


def main():
    """Launches public-facing user interface for dictation app."""
    # connect to database
    global DB
    client = MongoClient(
        f"mongodb://{getenv('MONGO_USERNAME')}:{getenv('MONGO_PASSWORD')}@mongo"
    )
    DB = client["recordings"]
    app.run(
        host="0.0.0.0",
        port=443,
        ssl_context=("certs/cert.pem", "certs/privkey.pem"),
        debug=True,
    )


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
    return (b"", 202)


@app.route("/record")
def record():
    """Returns recording page."""
    return render_template("makeRecordings.html")


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


@app.route("/download_audio/<oid_b62>")
def download_audio(oid_b62):
    """Returns an audio file attachment for user download."""
    oid = b62tooid(oid_b62)
    recording = DB["recordings"].find_one({"_id": oid})
    if recording is None:
        return redirect("/404")
    audio = pickle.loads(recording["audio"])
    return send_file(
        audio,
        download_name=f"{recording['name']}.opus",
        as_attachment=True,
        mimetype="audio/ogg",
    )


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


@app.route("/listings")
def listings():
    """Returns all recordings in descending date order for a user."""
    username = request.args.get("username")
    if username is None or username == "":
        return redirect("/404")
    recordings = list(
        DB["recordings"]
        .find({"username": username}, {"audio": 0, "transcript": 0})
        .sort("created", DESCENDING)
    )
    for recording in recordings:
        recording["id"] = oidtob62(recording["_id"])
        recording["created"] = recording["created"].strftime(
            "%A, %B %d %Y, %I:%M:%S %p"
        )
    return render_template("listings.html", username=username, recordings=recordings)


if __name__ == "__main__":
    main()
