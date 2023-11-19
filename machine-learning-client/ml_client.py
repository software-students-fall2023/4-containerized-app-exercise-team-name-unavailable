from flask import Flask, request

from bson.objectid import ObjectId

oidtob62 = lambda oid: base62.encodebytes(oid.binary)
b62tooid = lambda b62: ObjectId(base62.decodebytes(b62))

def main():
    pass

@app.route('/transcribe', methods=['POST'])
def transcribe():
    # Get object ID from request
    object_id = request.form['object_id']


if __name__ == '__main__':
    main()