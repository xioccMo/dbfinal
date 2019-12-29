from gtmd.app import db


class Book(db.Model):
    # 书籍的id
    book_id = db.Column(db.String, primary_key=True, index=True, unique=True)
    # 店铺id
    store_id = db.Column(db.String, index=True)
    # 书籍标题
    title = db.Column(db.String, nullable=False)
    # 书籍作者
    author = db.Column(db.String)
    # 书籍出版社
    publisher = db.Column(db.String)
    # 书籍原来的标题
    original_title = db.Column(db.String)
    # 书籍译者
    translator = db.Column(db.String)
    # 书籍出版年份
    pub_year = db.Column(db.String)
    # 书籍页数
    pages = db.Column(db.INTEGER)
    # 书籍价格
    price = db.Column(db.INTEGER, nullable=False)
    # 书籍装帧
    binding = db.Column(db.String)
    # 书籍ISBN
    isbn = db.Column(db.String)
    # 作者简介
    author_intro = db.Column(db.TEXT)
    # 书籍简介
    book_intro = db.Column(db.TEXT)
    # 书籍试读
    content = db.Column(db.String)
    # 书籍标签
    tags = db.Column(db.String)
    # 书籍图片
    # 注意这里的BLOB有两种方法， 一个是用db.TEXT
    # 另一是用json.dumps(string).encode('utf-8')
    pictures = db.Column(db.BLOB)
    # 书籍销量
    sales = db.Column(db.Integer, nullable=False, default=0)
    # 书籍库存
    stock_level = db.Column(db.INTEGER, nullable=False, default=0)
