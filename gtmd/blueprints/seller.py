from flask import Blueprint, request
from sqlalchemy import exc
from gtmd.app import db
from gtmd.models.Book import Book
from gtmd.models.Order import Order
from gtmd.models.Orderdetail import Orderdetail
from gtmd.models.Store import Store
from gtmd.models.User import User
from gtmd.tokenMethods import *
import json

seller_bp = Blueprint("seller", __name__, url_prefix="/seller")
# 卖家用户接口


# 创建店铺
@seller_bp.route("/create_store", methods=["GET", "POST"])
def create_store():
    """
    Response
    Status Code || Message || Judging Condition:
    401（自创）创建失败，用户名或token错误  token解析返回值为空（即token解析错误）或token解析成json格式后user_id对应的值与selle_id不符
    501 商铺ID已存在 商铺store_id属性为主键不能重复，通过捕捉exc.IntegrityError判断
    200 成功
    """
    token = jwtDecoding(request.headers.get("token"))
    store_id = request.json.get("store_id")
    seller_id = request.json.get("user_id")
    if token is None or token.json.get("user_id") != seller_id:
        return jsonify({"message": "创建失败，用户名或token错误"}), 401
    store = Store(store_id=store_id, seller_id=seller_id,)
    db.session.add(store)
    try:
        db.session.commit()
        return jsonify(({"message": "创建商铺成功"})), 200
    except exc.IntegrityError:
        return jsonify({"message": "商铺ID已存在"}), 501


# 填加书籍信息及描述
@seller_bp.route("/add_book", methods=["GET", "POST"])
def add_book():
    """
    Response
    Status Code || Message || Judging Condition:
    501 卖家用户ID不存在 查询User表中属性user_id为seller_id的元组，若返回值为空，则该卖家用户不存在
    502（自创） 添加失败，用户名或token错误 token解析返回值为空（即token解析错误）或token解析成json格式后user_id对应的值与seller_id不符
    503 商铺ID不存在 查询Store表中属性store_id为store_id的元组，若返回值为空，则该商铺ID不存在不存在
    504 图书ID已存在 每个书店中只能有唯一book_id的书籍，且考虑到主键问题咱（SqlAlchemy初试化每个表必须要有一个主键），对属性值book_id的构建为store_id + book_id构成，由于主键不能重复，通过捕捉exc.IntegrityError异常判断即可
    200 ok
    Attention:
    这里tags是用空格作为分隔符存储为字符串保存的
    这里Blob是用mediumblob类型，存储方法在Book.py里面有两种方法说明
    """
    token = jwtDecoding(request.headers.get("token"))
    seller_id = request.json.get("user_id")
    store_id = request.json.get("store_id")
    book_info = request.json.get("book_info")
    stock_level = request.json.get("stock_level")
    user = User.query.filter_by(user_id=seller_id).first()
    if user is None:
        return jsonify({"message": "卖家用户ID不存在"}), 501
    if token is None or token.json.get("user_id") != seller_id:
        return jsonify({"message": "添加失败，用户名或token错误"}), 502
    store = Store.query.filter_by(seller_id=seller_id, store_id=store_id).first()
    if store is None:
        return jsonify({"message": "商铺ID不存在"}), 503
    book = Book(
        # 这里做一点冗余处理，主要实现不同店铺可以加相同id的商品，而同一个店铺不行，否则测试过不了
        book_id=store_id + "|" + book_info["id"],
        store_id=store_id,
        title=book_info["title"],
        author=book_info["author"],
        publisher=book_info["publisher"],
        original_title=book_info["original_title"],
        translator=book_info["translator"],
        pub_year=book_info["pub_year"],
        pages=book_info["pages"],
        price=book_info["price"],
        binding=book_info["binding"],
        isbn=book_info["isbn"],
        author_intro=book_info["author_intro"],
        book_intro=book_info["book_intro"],
        content=book_info["content"],
        tags=" ".join(book_info["tags"]),
        pictures=json.dumps("".join(book_info["pictures"])).encode('utf-8'),
        stock_level=stock_level
    )
    db.session.add(book)
    try:
        db.session.commit()
        return jsonify({"message": "ok"}), 200
    except exc.IntegrityError:
        return jsonify({"message": "图书ID已存在"}), 504


# 增加库存
@seller_bp.route("add_stock_level", methods=["GET", "POST"])
def update_stock_level():
    """
    Response
    Status Code || Message || Judging Condition:
    501 卖家用户ID不存在 查询User表中属性user_id为seller_id的元组，若返回值为空，则该卖家用户不存在
    502（自创） 添加失败，用户名或token错误 token解析返回值为空（即token解析错误）或token解析成json格式后user_id对应的值与seller_id不符
    503 商铺ID不存在 查询Store表中属性store_id为store_id的元组，若返回值为空，则该商铺ID不存在不存在
    504 图书ID不存在 查询Book表中属性book_id为book_id的元组，若返回值为空，则该书籍ID不存在不存在
    200 ok
    """
    token = jwtDecoding(request.headers.get("token"))
    seller_id = request.json.get("user_id")
    store_id = request.json.get("store_id")
    book_id = request.json.get("book_id")
    add_stock_level = request.json.get("add_stock_level")
    user = User.query.filter_by(user_id=seller_id).first()
    if user is None:
        return jsonify({"message": "卖家用户ID不存在"}), 501
    if token is None or token.json.get("user_id") != seller_id:
        return jsonify({"message": "添加失败，用户名或token错误"}), 502
    store = Store.query.filter_by(seller_id=seller_id, store_id=store_id).first()
    if store is None:
        return jsonify({"message": "商铺ID不存在"}), 503
    book = Book.query.filter_by(store_id=store_id, book_id=store_id + "|" + book_id).first()
    if book is None:
        return jsonify({"message": "图书ID不存在"}), 504
    book.stock_level += add_stock_level
    db.session.commit()
    return jsonify({"message": "ok"}), 200


@seller_bp.route("change_unreceived", methods=["POST"])
def change_unreceived():
    # 这里是按照淘宝的设计，只针对单个订单进行发货处理
    token = jwtDecoding(request.headers.get("token"))
    seller_id = request.json.get("user_id")
    store_id = request.json.get("store_id")
    order_id = request.json.get("order_id")
    user = User.query.filter_by(user_id=seller_id).first()
    if user is None:
        return jsonify({"message": "卖家用户ID不存在"}), 501
    if token is None or token.json.get("user_id") != seller_id:
        return jsonify({"message": "修改状态失败，用户名或token错误"}), 502
    store = Store.query.filter_by(seller_id=seller_id, store_id=store_id).first()
    if store is None:
        return jsonify({"message": "商铺ID不存在"}), 503
    order = Order.query.filter_by(order_id=order_id, store_id=store_id).first()
    if order is None:
        return jsonify({"message": "订单查询失败"}), 504
    if order.status != "paid":
        return jsonify({"message": "该订单物品状态不是待发货状态，无法切换为发货状态"}), 506
    order.status = "unreceived"
    db.session.commit()
    return jsonify({"message": "ok"}), 200

