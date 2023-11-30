from flask import Flask, render_template, request, redirect

from os import getenv
from bson.objectid import ObjectId

import os
import base64
import pymongo
import datetime
import requests
import pickle

oidtob62 = lambda oid: base64.encodebytes(oid.binary)
b62tooid = lambda b62: ObjectId(base64.decodebytes(b62))

template_dir = os.path.abspath("/templates")
static_dir = os.path.abspath("/static")
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
    app.run(host="0.0.0.0", port=443, ssl_context=("cert.pem", "key.pem"))


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
            "date": datetime.datetime.utcnow(),
        }
    )
    requests.post(
        "http://ml:80/transcribe",
        data={"id": oidtob62(oid)},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=5,  # 5 seconds, should be good enough
    )
    return 202


if __name__ == "__main__":
    main()
