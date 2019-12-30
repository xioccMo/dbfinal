import base64
import datetime
import random
import uuid

import sqlalchemy
from flask import Blueprint, request
from sqlalchemy import text

from gtmd.app import db
from gtmd.config import SQLALCHEMY_DATABASE_URI
from gtmd.models.Book import Book
from gtmd.models.Order import Order
from gtmd.models.Orderdetail import Orderdetail
from gtmd.models.Store import Store
from gtmd.models.User import User
from gtmd.models.Forunpaidorder import Forunpaidorder
from gtmd.models.Foruncommentorder import Foruncommentorder

from gtmd.tokenMethods import *

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
    token = jwtDecoding(request.headers.get("token"))  # token: 标记
    buyer_id = request.json.get("user_id")
    user = User.query.filter_by(user_id=buyer_id).first()  # FIRST() 函数返回指定的列中第一个记录的值 user_id
    if user is None:
        return jsonify({"message": "买家用户ID不存在"}), 501
    if token is None or buyer_id != token.json.get("user_id"):
        return jsonify({"message": "用户名或token错误"}), 502
    store_id = request.json.get("store_id")
    store = Store.query.filter_by(store_id=store_id).first()
    if store is None:
        return jsonify({"message": "商铺ID不存在"}), 503
    order_id = str(uuid.uuid1())
    order = Order(order_id=order_id, store_id=store_id, buyer_id=buyer_id, status="unpaid")
    db.session.add(order)
    db.session.commit()
    for item in request.json.get("books"):
        book_id = item["id"]
        count = item["count"]
        book = Book.query.filter_by(book_id=store_id + "|" + book_id).first()
        if book is None or book.stock_level < count:
            db.session.rollback()
            Order.query.filter_by(order_id=order_id).delete()
            db.session.commit()
            if book is None:
                return jsonify({"message": "购买的图书不存在"}), 504
            elif book.stock_level < count:
                return jsonify({"message": "商品库存不足"}), 505
        book.stock_level -= count
        orderdetail = Orderdetail(orderdetail_id=str(uuid.uuid1()), order_id=order_id, book_id=store_id + "|" + book_id,
                                  count=count, price=book.price)
        db.session.add(orderdetail)
    forunpaidorder = Forunpaidorder(order_id=order_id)
    db.session.add(forunpaidorder)
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
    elif order.status != "unpaid" or (datetime.datetime.now() - order.createtime).total_seconds() >= 10:
        return jsonify({"message": "当前订单状态无法支付"}), 502
    orderdetails = Orderdetail.query.filter_by(order_id=order_id).all()
    total = 0
    for orderdetail in orderdetails:
        total += orderdetail.price * orderdetail.count
    # 这里需要修改说明
    if total > user.value:
        db.session.rollback()
        return jsonify({"message": "账户余额不足"}), 503
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


@buyer_bp.route("/change_received", methods=["GET", "POST"])
def change_received():
    token = jwtDecoding(request.headers.get("token"))
    buyer_id = request.json.get("user_id")
    order_id = request.json.get("order_id")
    user = User.query.filter_by(user_id=buyer_id).first()
    if user is None:
        return jsonify({"message": "买家用户ID不存在"}), 501
    if token is None or buyer_id != token.json.get("user_id"):
        return jsonify({"message": "用户名或token错误"}), 502
    order = Order.query.filter_by(buyer_id=buyer_id, order_id=order_id).first()
    if order is None:
        return jsonify({"message": "当前用户没有该订单或订单不存在"}), 503
    elif order.status != "unreceived":
        return jsonify({"message": "当前订单物品状态不为待发货，无法切换为收货状态"}), 504

    order.status = "received"
    for orderdetail in order.orderdetail:
        orderdetail.book_info.sales + orderdetail.count
    db.session.add(Foruncommentorder(order_id=order_id))
    db.session.commit()
    return jsonify({"message": "ok"}), 200


@buyer_bp.route("/cancel_order", methods=["POST"])
def cancel_order():
    token = jwtDecoding(request.headers.get("token"))
    buyer_id = request.json.get("user_id")
    order_id = request.json.get("order_id")
    user = User.query.filter_by(user_id=buyer_id).first()
    if user is None:
        return jsonify({"message": "买家用户不存在"}), 501
    if token is None or buyer_id != token.json.get("user_id"):
        return jsonify({"message": "用户名或token错误"}), 502
    order = Order.query.filter_by(buyer_id=buyer_id, order_id=order_id).first()
    if order is None:
        return jsonify({"message": "当前用户没有该订单或订单不存在"}), 503
    elif order.status != "unpaid" and order.status != "paid":
        return jsonify({"message": "当前订单无法取消"}), 504
    orderdetails = Orderdetail.query.filter_by(order_id=order_id).all()
    for orderdetail in orderdetails:
        book = Book.query.filter_by(book_id=orderdetail.book_id).first()
        book.stock_level += orderdetail.count
        if order.status == "paid":
            user.value += orderdetail.count * orderdetail.price
    order.status = "canceled"
    db.session.commit()
    return jsonify({"message": "取消订单成功"}), 200


@buyer_bp.route("/track_order_by_order_id", methods=["POST"])
def track_order_by_order_id():
    token = jwtDecoding(request.headers.get("token"))
    buyer_id = request.json.get("user_id")
    order_id = request.json.get("order_id")
    user = User.query.filter_by(user_id=buyer_id).first()
    if user is None:
        return jsonify({"message": "买家用户不存在"}), 501
    if token is None or buyer_id != token.json.get("user_id"):
        return jsonify({"message": "用户名或token错误"}), 502
    order = Order.query.filter_by(buyer_id=buyer_id, order_id=order_id).first()
    if order is None:
        return jsonify({"message": "当前用户没有该订单或订单不存在"}), 503
    order_info = {
        "order_id": order_id,
        "createtime": order.createtime,
        "store_id": order.store_id,
        "orderdetail": []
    }
    items = Orderdetail.query.filter_by(order_id=order_id).all()
    total = 0
    for item in items:
        order_info["orderdetail"].append(
            {
                "orderdetail_id": item.orderdetail_id,
                "book_id": item.book_id,
                "book_title": item.book_info.title,
                "book_author": item.book_info.author,
                "count": item.count,
                "unit_price": item.price,
            }
        )
        total += item.count * item.price
    order_info["total_price"] = total
    order_info["message"] = "ok"
    return jsonify(order_info), 200


@buyer_bp.route("/track_order", methods=["POST"])
def track_order():
    token = jwtDecoding(request.headers.get("token"))
    buyer_id = request.json.get("user_id")
    user = User.query.filter_by(user_id=buyer_id).first()
    if user is None:
        return jsonify({"message": "买家用户不存在"}), 501
    if token is None or buyer_id != token.json.get("user_id"):
        return jsonify({"message": "用户名或token错误"}), 502
    unaccomplishdorders = Order.query.filter(Order.buyer_id == buyer_id,
                                             ~Order.status.in_(["canceled", "received"])).order_by(
        Order.createtime.desc()).all()
    accomplishorders = Order.query.filter(Order.buyer_id == buyer_id,
                                          Order.status.in_(["canceled", "received"])).order_by(
        Order.createtime.desc()).all()

    json = {"message": "ok", "order": []}
    for order in unaccomplishdorders + accomplishorders:
        order_info = {
            "order_id": order.order_id,
            "createtime": order.createtime,
            "store_id": order.store_id,
            "status": order.status,
            "orderdetail": []
        }
        total = 0
        for orderdetail in order.orderdetail:
            order_info["orderdetail"].append(
                {
                    "orderdetail_id": orderdetail.orderdetail_id,
                    "book_id": orderdetail.book_id,
                    "book_title": orderdetail.book_info.title,
                    "count": orderdetail.count,
                    "unit_price": orderdetail.price
                }
            )
            total += orderdetail.count * orderdetail.price
        order_info["total_price"] = total
        json["order"].append(order_info)
    return jsonify(json), 200


@buyer_bp.route("/add_comment", methods=["POST"])
def add_comment():
    token = jwtDecoding(request.headers.get("token"))
    buyer_id = request.json.get("user_id")
    orderdetail_id = request.json.get("orderdetail_id")
    star = request.json.get("star")
    content = request.json.get("content")
    if star <= 0 or star > 5:
        return jsonify({"message": "评分参数错误"}), 506
    if content == "":
        return jsonify({"message": "评论不能为空"}), 507
    user = User.query.filter_by(user_id=buyer_id).first()
    if user is None:
        return jsonify({"message": "买家用户不存在"}), 501
    if token is None or buyer_id != token.json.get("user_id"):
        return jsonify({"message": "用户名或token错误"}), 502
    orderdetail = Orderdetail.query.filter_by(orderdetail_id=orderdetail_id).first()
    if orderdetail is None:
        return jsonify({"message": "订单物品出错，请重试"}), 503
    elif orderdetail.order_info.status != "received":
        return jsonify({"message": "该物品对应订单还未收货，无法评价"}), 504
    elif orderdetail.status == "commented":
        return jsonify({"message": "该物品已被评论，评论失败"}), 505

    orderdetail.status = "commented"
    orderdetail.createtime = datetime.datetime.now()
    orderdetail.star = star
    orderdetail.content = content
    db.session.commit()
    return jsonify({"message": "ok"}), 200


@buyer_bp.route("/update_comment", methods=["POST"])
def update_comment():
    token = jwtDecoding(request.headers.get("token"))
    buyer_id = request.json.get("user_id")
    orderdetail_id = request.json.get("orderdetail_id")
    content = request.json.get("content")
    if content == "":
        return jsonify({"message": "评论不能为空"}), 505
    user = User.query.filter_by(user_id=buyer_id).first()
    if user is None:
        return jsonify({"message": "买家用户不存在"}), 501
    if token is None or buyer_id != token.json.get("user_id"):
        return jsonify({"message": "用户名或token错误"}), 502
    orderdetail = Orderdetail.query.filter_by(orderdetail_id=orderdetail_id).first()
    if orderdetail is None:
        return jsonify({"message": "订单物品出错，请重试"}), 503
    elif orderdetail.status != "commented":
        return jsonify({"message": "该物品未被评论，评论无法更新"}), 504
    orderdetail.content = content
    db.session.commit()
    return jsonify({"message": "ok"}), 200


@buyer_bp.route("/get_comment_by_book_id", methods=["POST"])
def get_comment_by_book_id():
    store_id = request.json.get("store_id")
    book_id = request.json.get("book_id")

    store = Store.query.filter_by(store_id=store_id).first()
    if store is None:
        return jsonify({"message": "商店不存在"}), 501

    book = Book.query.filter_by(book_id=store_id + "|" + book_id).first()

    if book is None:
        return jsonify({"message": "该图书不存在"}), 502
    orderdetails = Orderdetail.query.filter_by(book_id=book_id).order_by(Orderdetail.createtime.desc()).limit(500).all()
    json = {
          "comment": []
    }
    for orderdetail in orderdetails:
        json["comment"].append({
            "createtime": orderdetail.createtime,
            "buyer_id": orderdetail.buyer_id,
            "star":  orderdetail.star,
            "content": orderdetail.content,
        })
    return jsonify(json), 200


@buyer_bp.route("/search_book_store", methods=["POST"])
def search_book_store():
    token = jwtDecoding(request.headers.get("token"))
    buyer_id = request.json.get("user_id")
    store_id = request.json.get("store_id")
    key_word = request.json.get("key_word")
    user = User.query.filter_by(user_id=buyer_id).first()

    if user is None:
        return jsonify({"message": "买家用户不存在"}), 501
    if token is None or buyer_id != token.json.get("user_id"):
        return jsonify({"message": "用户名或token错误"}), 502

    json = {
        "search_book_result": []
    }
    book_list = {}
    engine = db.create_engine(SQLALCHEMY_DATABASE_URI, {})
    conn = engine.connect()
    try:
        conn.execute("CREATE FULLTEXT INDEX "
                     "fulltext_index ON book(title,book_intro) with parser ngram;")
    except sqlalchemy.exc.InternalError:
        pass
    finally:
        sql = text("SELECT * FROM book "
                   "WHERE MATCH (title,book_intro) AGAINST ('%s' IN NATURAL LANGUAGE MODE)"
                   "AND store_id='%s';" % (key_word, store_id))
        cursor = conn.execute(sql)
        for row in cursor:
            book_list["book_id"] = row[0]
            book_list["store_id"] = row[1]
            book_list["title"] = row[2]
            book_list["author"] = row[3]
            book_list["publisher"] = row[4]
            book_list["original_title"] = row[5]
            book_list["translator"] = row[6]
            book_list["pub_year"] = row[7]
            book_list["pages"] = row[8]
            book_list["price"] = row[9]
            book_list["binding"] = row[10]
            book_list["isbn"] = row[11]
            book_list["author_intro"] = row[12]
            book_list["book_intro"] = row[13]
            book_list["content"] = row[14]
            book_list["tags"] = row[15]
            book_list["picture"] = row[16]
            json["search_book_result"].append(book_list)
    return jsonify(json), 200


@buyer_bp.route("/search_book_site", methods=["POST"])
def search_book_site():
    token = jwtDecoding(request.headers.get("token"))
    buyer_id = request.json.get("user_id")
    key_word = request.json.get("key_word")
    user = User.query.filter_by(user_id=buyer_id).first()

    if user is None:
        return jsonify({"message": "买家用户不存在"}), 501
    if token is None or buyer_id != token.json.get("user_id"):
        return jsonify({"message": "用户名或token错误"}), 502

    json = {
        "search_book_result": []
    }
    book_list = {}
    engine = db.create_engine(SQLALCHEMY_DATABASE_URI, {})
    conn = engine.connect()
    try:
        conn.execute("CREATE FULLTEXT INDEX "
                     "fulltext_index ON book(title,book_intro) with parser ngram;")
    except sqlalchemy.exc.InternalError:
        pass
    finally:
        sql = text("SELECT * FROM book WHERE MATCH (title,book_intro) AGAINST ('%s' IN NATURAL LANGUAGE MODE);" % key_word)
        cursor = conn.execute(sql)
        for row in cursor:
            book_list["book_id"] = row[0]
            book_list["store_id"] = row[1]
            book_list["title"] = row[2]
            book_list["author"] = row[3]
            book_list["publisher"] = row[4]
            book_list["original_title"] = row[5]
            book_list["translator"] = row[6]
            book_list["pub_year"] = row[7]
            book_list["pages"] = row[8]
            book_list["price"] = row[9]
            book_list["binding"] = row[10]
            book_list["isbn"] = row[11]
            book_list["author_intro"] = row[12]
            book_list["book_intro"] = row[13]
            book_list["content"] = row[14]
            book_list["tags"] = row[15]
            book_list["picture"] = row[16]
            json["search_book_result"].append(book_list)
    return jsonify(json), 200
