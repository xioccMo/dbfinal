from gtmd.app import db


class Orderdetail(db.Model):
    # id
    orderdetail_id = db.Column(db.String,  primary_key=True, index=True, nullable=False, unique=True)
    # 订单id
    order_id = db.Column(db.String, db.ForeignKey("order.order_id"), index=True, nullable=False)
    # 书籍id
    book_id = db.Column(db.String, db.ForeignKey("book.book_id"), index=True, nullable=False,)
    # 书籍数目
    count = db.Column(db.Integer, nullable=False)
    # 书籍下单时价格
    price = db.Column(db.Integer, nullable=False)
    # 书籍评分
    star = db.Column(db.Integer, nullable=True, default=0)
    # 书籍评价
    comment = db.Column(db.TEXT, nullable=True)

    book_info = db.relationship("Book", backref="book_info")
