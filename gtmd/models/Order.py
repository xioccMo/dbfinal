from gtmd.app import db
import datetime


class Order(db.Model):
    # 订单id
    order_id = db.Column(db.String, primary_key=True, index=True, nullable=False)
    # 用户id
    buyer_id = db.Column(db.String, index=True, nullable=False)
    # 商店id
    store_id = db.Column(db.String, index=True, nullable=False)
    # 创建时间
    createtime = db.Column(db.DATETIME, default=datetime.datetime.now, nullable=False)
    # 订单状态
    status = db.Column(db.String, nullable=False)

    orderdetail = db.relationship("Orderdetail", backref="orderdetail")
