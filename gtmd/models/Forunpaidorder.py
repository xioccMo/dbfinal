from gtmd.app import db
import datetime


class Forunpaidorder(db.Model):
    # 订单id
    id = db.Column(db.Integer, primary_key=True, index=True, nullable=False, autoincrement=True)
    order_id = db.Column(db.String, db.ForeignKey("order.order_id"), index=True, nullable=False)