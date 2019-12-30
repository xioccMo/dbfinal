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
    # 商品状态
    status = db.Column(db.String, default="uncommented", nullable=False)
    # 评论时间
    createtime = db.Column(db.DATETIME, nullable=True)
    # 评论分数
    star = db.Column(db.Integer, nullable=True)
    # 评论内容
    content = db.Column(db.Integer, nullable=True)

    book_info = db.relationship("Book", backref="book_info")
    order_info = db.relationship("Order", backref="order_info")
