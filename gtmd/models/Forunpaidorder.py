import threading
import time

from gtmd.app import db
import datetime


class Forunpaidorder(db.Model):
    # 订单id
    id = db.Column(db.Integer, primary_key=True, index=True, nullable=False, autoincrement=True)
    order_id = db.Column(db.String, db.ForeignKey("order.order_id"), index=True, nullable=False)
    order = db.relationship("Order", backref="Order")


def unpaidMonitor():
    while True:
        forunpaidorder = db.session.query(Forunpaidorder).order_by(Forunpaidorder.id).first()
        if forunpaidorder is None:
            db.session.close()
            continue
        elif forunpaidorder.order.status != "unpaid":
            db.session.delete(forunpaidorder)
            db.session.commit()
            continue
        elif (datetime.datetime.now() - forunpaidorder.order.createtime).total_seconds() < 10:
            db.session.close()
            continue
        forunpaidorder.order.status = "canceled"
        db.session.delete(forunpaidorder)
        db.session.commit()


thread = threading.Thread(target=unpaidMonitor)
thread.setDaemon(True)
thread.start()