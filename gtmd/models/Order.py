from gtmd.app import db


class Order(db.Model):
    # 订单id
    order_id = db.Column(db.String, primary_key=True, index=True, nullable=False)
    # 用户id
    buyer_id = db.Column(db.String, index=True, nullable=False)
    # 商店id
    store_id = db.Column(db.String, index=True, nullable=False)
    # 订单status
    status = db.Column(db.String, nullable=False, default="unpay")