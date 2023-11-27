from flask import Flask, render_template, request, redirect

from os import getenv
from bson.objectid import ObjectId

import os
import base64
import pymongo
import datetime

oidtob62 = lambda oid: base64.encodebytes(oid.binary)
b62tooid = lambda b62: ObjectId(base64.decodebytes(b62))

template_dir = os.path.abspath('/templates')
static_dir = os.path.abspath('/static')
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

DB = None

def main():
    # connect to database
    global DB
    DB = pymongo.MongoClient("mongodb://mongo:27017",
                            username=getenv("MONGO_USER"),
                            password=getenv("MONGO_PASSWORD"),
    )

    app.run(ssl_context=('cert.pem', 'key.pem'))

if __name__ == "__main__":
    main()
    