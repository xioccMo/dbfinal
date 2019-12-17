from flask import Blueprint, request
from sqlalchemy import exc
from gtmd.app import db
from gtmd.models.User import User
from gtmd.tokenMethods import *

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Response
    Status Code || Message || Judging Condition:
    401 登录失败，用户名或密码错误 通过user_id 和 password查询User表，返回的查询结果为空
    200 ok

    Attention：
    返回的json中要返回其token（其会在头部headers传入这个token用以各种请求的授权和验证）
    """
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
    """
    Response
    Status Code || Message || Judging Condition:
    501 注册失败，用户名重复  插入失败（因为主键不能重复），捕捉到exc.IntegrityError异常
    200 ok
    """
    user_id = request.json.get("user_id")
    password = request.json.get("password")
    user = User(user_id=user_id, password=password)
    db.session.add(user)
    try:
        db.session.commit()
    except exc.IntegrityError:
        return jsonify({{'message': '注册失败，用户名重复'}}), 501
    return jsonify({'message': 'ok'}), 200


@auth_bp.route('/unregister', methods=['GET', 'POST'])
def unregister():
    """
    Response
    Status Code || Message || Judging Condition:
    401 注销失败，用户名不存在或密码不正确  通过user_id 和 password查询User表，返回的查询结果为空
    200 ok
    """
    user_id = request.json.get("user_id")
    password = request.json.get("password")
    user = User.query.filter_by(user_id=user_id, password=password)
    if user.first() is not None:
        user.delete()
        db.session.commit()
    else:
        return jsonify({"message": "注销失败，用户名不存在或密码不正确"}), 401
    return jsonify({"message":"ok"})


@auth_bp.route('/password', methods=['GET', 'POST'])
def password():
    """
    Response
    Status Code || Message || Judging Condition:
    401 更改密码失败  通过user_id 和 password查询User表，返回的查询结果为空
    200 ok
    """
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
    """
    Response
    Status Code || Message || Judging Condition:
    401 登出失败，用户名或token错误  token解析返回值为空（即token解析错误）或token解析成json格式后user对应的值与user_id不符
    200 ok
    """
    user_id = request.json.get("user_id")
    token = jwtDecoding(request.headers.get("token"))
    if token is None or token.json.get("user_id") != user_id:
        return jsonify({"message": "登出失败，用户名或token错误"}), 401
    return jsonify({"message": "ok"}), 200