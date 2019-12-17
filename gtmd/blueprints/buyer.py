from flask import Blueprint, request
from sqlalchemy import exc
from gtmd.app import db
from gtmd.models.Book import Book
from gtmd.models.Order import Order
from gtmd.models.Orderdetail import Orderdetail
from gtmd.models.Store import Store
from gtmd.models.User import User
from gtmd.tokenMethods import *
import uuid
buyer_bp = Blueprint("buyer", __name__, url_prefix="/buyer")


@buyer_bp.route("/new_order", methods=["GET", "POST"])
def new_order():
    """
    Response
    Status Code In Order:
    501 买家用户ID不存在 查询User表中属性user_id为user_id的元祖，若返回值为空，则该user_id无效
    502 用户名或token错误 token解析返回值为空（即token解析错误）或token解析成json格式后user_id对应的值与buyer_id不符
    503 商户ID不存在 查询Store表中属性store_id为store_id的元祖，若返回值为空，则该store_id无效
    504 购买的图书不存在 查询Book表中属性Book_id为book_id的元祖，若返回值为空，则该购买的图书不存在
    505 商品库存不足 查询Book表中属性book_id为book_id，若返回值不为空但库存量小于要购买书籍的量，则该购买书籍的库存不足
    200 order_id
    Attention:
    1、返回的是order_id
    2、由于外键限制，在创建订单详细的元祖之前，得先在表Order中创建属性order_id为order_id的订单项
    3、当遇到503和504错误，得先用session.rollback进行回滚，再删除之前创建的订单项然后返回
    """
    token = jwtDecoding(request.headers.get("token"))
    buyer_id = request.json.get("user_id")
    user = User.query.filter_by(user_id=buyer_id).first()
    if user is None:
        return jsonify({"message": "买家用户ID不存在"}), 501
    if token is None or buyer_id != token.json.get("user_id"):
        return jsonify({"message": "用户名或token错误"}), 502
    store_id = request.json.get("store_id")
    store = Store.query.filter_by(store_id=store_id).first()
    if store is None:
        return jsonify({"message": "商铺ID不存在"}), 503
    order_id = str(uuid.uuid1())
    order = Order(order_id=order_id, store_id=store_id, buyer_id=buyer_id, status="unpay")
    db.session.add(order)
    db.session.commit()
    for item in request.json.get("books"):
        book_id = item["id"]
        count = item["count"]
        book = Book.query.filter_by(book_id=store_id+book_id).first()
        if book is None or book.stock_level < count:
            db.session.rollback()
            Order.query.filter_by(order_id=order_id).delete()
            db.session.commit()
            if book is None:
                return jsonify({"message": "购买的图书不存在"}), 504
            elif book.stock_level < count:
                return jsonify({"message": "商品库存不足"}), 505
        book.stock_level -= count
        order = Orderdetail(id=str(uuid.uuid1()), order_id=order_id, book_id=store_id+book_id, count=count, price=book.price)
        db.session.add(order)
    db.session.commit()
    return jsonify({"order_id": order_id}), 200


@buyer_bp.route("/payment", methods=["GET", "POST"])
def payment():
    """
    Response
    Status Code In Order:
    501 无效参数 查询Order表中属性order_id为order_id的元祖，若返回值为空，则该order_id无效
    401 授权失败 查询User表中属性user_id为buyer_id和属性password为password的元组，若返回值为空，则该消费者用户不存在
    502 账户余额不足 判断账户的余额是否小于账单需支付的金额
    200 ok
    """
    buyer_id = request.json.get("user_id")
    order_id = request.json.get("order_id")
    password = request.json.get("password")
    user = User.query.filter_by(user_id=buyer_id, password=password).first()
    if user is None:
        return jsonify({"message": "授权失败"}), 401
    order = Order.query.filter_by(order_id=order_id).first()
    if order is None:
        return jsonify({"message": "无效参数"}), 501
    orderitems = Orderdetail.query.filter_by(order_id=order_id).all()
    total = sum([orderitem.price * orderitem.count for orderitem in orderitems])
    if total > user.value:
        return jsonify({"message": "账户余额不足"}), 502
    user.value -= total
    order.status = "paid"
    db.session.commit()
    return jsonify({"message": "ok"}), 200


@buyer_bp.route("/add_funds", methods=["GET", "POST"])
def add_funds():
    """
    Response
    Status Code In Order:
    501 无效参数 判断add_value（以分为单位）是否为整数值
    401 授权失败 查询User表中属性user_id为buyer_id和属性password为password的元组，若返回值为空，则该消费者用户不存在
    200 ok
    """
    user_id = request.json.get("user_id")
    password = request.json.get("password")
    add_value = request.json.get("add_value")
    if not isinstance(add_value, int):
        return jsonify({"message": "无效参数"}), 501
    user = User.query.filter_by(user_id=user_id, password=password).first()
    if user is None:
        return jsonify({"message": "授权失败"}), 401
    user.value += add_value
    db.session.commit()
    return jsonify({"message": "ok"}), 200

