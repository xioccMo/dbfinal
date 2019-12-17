from gtmd.app import db


class Orderdetail(db.Model):
    # id
    id = db.Column(db.String,  primary_key=True, index=True, nullable=False, unique=True)
    # 订单id
    order_id = db.Column(db.String,  index=True, nullable=False)
    # 书籍id
    book_id = db.Column(db.String, index=True, nullable=False)
    # 书籍数目
    count = db.Column(db.Integer, nullable=False)
    # 书籍下单时价格
    price = db.Column(db.Integer, nullable=False)
