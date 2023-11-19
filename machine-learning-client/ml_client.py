import base64
import base62
from flask import Flask, request
from os import getenv
import whisper

from bson.objectid import ObjectId

oidtob62 = lambda oid: base64.encodebytes(oid.binary)
b62tooid = lambda b62: ObjectId(base62.decodebytes(b62))

def main():
    pass

@app.route('/transcribe', methods=['POST'])
def transcribe():
    # Get object ID from request
    oid = b62tooid(request.form['id'])
    # Get pickled opus audio data from database
    pass # TODO: blocked on database connection details
    

if __name__ == '__main__':
    main()