from gtmd.app import db


class Store(db.Model):
    # 用户id
    seller_id = db.Column(db.String, unique=True, index=True, nullable=False)
    # 商铺id
    store_id = db.Column(db.String, primary_key=True, unique=True, index=True, nullable=False)