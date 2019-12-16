from flask import Blueprint, jsonify, request
from sqlalchemy import exc
from gtmd.app import db
from gtmd.models.User import User
import jwt

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

SECRET_KEY = "CaiXukun"
algorithm = "HS256"


def jwtEncoding(jsonstring):
    return jwt.encode(jsonstring, key=SECRET_KEY, algorithm=algorithm)


def jwtDecoding(token):
    try:
        return jsonify(jwt.decode(token, key=SECRET_KEY, algorithm=algorithm))
    except jwt.DecodeError:
        return None

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    user_id = request.json.get("user_id")
    password = request.json.get("password")
    terminal = request.json.get("terminal")
    user = User.query.filter_by(user_id=user_id, password=password).first()
    if user is None:
        return jsonify({"message": "登录失败，用户名或密码错误", "token": ""}), 401
    user.terminal = terminal
    db.session.commit()
    token = jwtEncoding(
        {
            "user_id": user_id,
            "terminal": terminal
        }
    )
    return jsonify({"message": "ok", "token": token}), 200


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    user_id = request.json.get("user_id")
    password = request.json.get("password")
    user = User(id=0, user_id=user_id, password=password)
    db.session.add(user)
    try:
        db.session.commit()
    except exc.SQLAlchemyError:
        return jsonify({{'message': '注册失败，用户名重复'}}), 501
    return jsonify({'message': 'ok'}), 200


@auth_bp.route('/unregister', methods=['GET', 'POST'])
def unregister():
    user_id = request.json.get("user_id")
    password = request.json.get("password")
    user = User.query.filter_by(user_id=user_id, password=password)
    if user.first() is not None:
        user.delete()
        db.session.commit()
    else:
        return jsonify({'message', '注销失败，用户名不存在或密码不正确'}),
    return jsonify({'message':200})


@auth_bp.route('/password', methods=['GET', 'POST'])
def password():
    user_id = request.json.get("user_id")
    oldPassword = request.json.get("oldPassword")
    newPassword = request.json.get("newPassword")
    user = User.query.filter_by(user_id=user_id, password=oldPassword).first()
    if user is None:
        return jsonify({"message": "更改密码失败"}), 401
    user.password = newPassword
    db.session.commit()
    return jsonify({"message": "ok"}), 200


@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    user_id = request.json.get("user_id")
    token = jwtDecoding(request.headers.get("token"))
    if token is None or token.json.get("user_id") != user_id:
        return jsonify({"message": "登出失败，用户名或token错误"}), 401
    return jsonify({"message": "ok"}), 200