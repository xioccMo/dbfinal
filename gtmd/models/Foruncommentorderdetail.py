import threading
import time

from gtmd.app import db
import datetime


class Foruncommentorderdetail(db.Model):
    # 订单id
    id = db.Column(db.Integer, primary_key=True, index=True, nullable=False, autoincrement=True)
    orderdetail_id = db.Column(db.String, db.ForeignKey("orderdetail.orderdetail_id"), index=True, nullable=False)
    orderdetail = db.relationship("Orderdetail", backref="Orderdetail")


def uncommentMonitor():
    while True:
        foruncommentorderdetail = Foruncommentorderdetail.query.order_by(Foruncommentorderdetail.id).first()
        if foruncommentorderdetail is None:
            db.session.close()
            continue
        elif foruncommentorderdetail.orderdetail.status != "uncommented":
            db.session.delete(foruncommentorderdetail)
            db.session.commit()
            continue
        elif (datetime.datetime.now() - foruncommentorderdetail.orderdetail.receivedtime).total_seconds() < 10:
            db.session.close()
            continue
        foruncommentorderdetail.orderdetail.status = "commented"
        foruncommentorderdetail.orderdetail.createtime = datetime.datetime.now()
        foruncommentorderdetail.orderdetail.star = 5
        foruncommentorderdetail.orderdetail.content = "蔡徐坤比心般默认好评！"
        db.session.delete(foruncommentorderdetail)
        db.session.commit()


thread = threading.Thread(target=uncommentMonitor)
thread.setDaemon(True)
thread.start()