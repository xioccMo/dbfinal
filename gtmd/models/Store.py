from gtmd.app import db


class Store(db.Model):
    # id
    id = db.Column(db.INTEGER, primary_key=True, unique=True, index=True, nullable=False, autoincrement=True)
    # 用户id
    seller_id = db.Column(db.String, unique=True, index=True, nullable=False)
    # 商铺id
    store_id = db.Column(db.String, nullable=False)