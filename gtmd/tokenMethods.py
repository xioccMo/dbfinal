from flask import jsonify
import jwt
SECRET_KEY = "CaiXukun"
algorithm = "HS256"


def jwtEncoding(jsonstring):
    return jwt.encode(jsonstring, key=SECRET_KEY, algorithm=algorithm)


def jwtDecoding(token):
    try:
        return jsonify(jwt.decode(token, key=SECRET_KEY, algorithm=algorithm))
    except jwt.DecodeError:
        return None