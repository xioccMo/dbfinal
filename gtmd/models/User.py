from gtmd.app import db


class User(db.Model):
    # 用户名
    user_id = db.Column(db.String(255), primary_key=True, unique=True, index=True, nullable=False)
    # 用户密码
    password = db.Column(db.String(255), nullable=False)
    # 用户登录设备
    terminal = db.Column(db.String(255), nullable=False, default="0000000")
    # 用户余额
    value = db.Column(db.Integer, nullable=False, default=0)
