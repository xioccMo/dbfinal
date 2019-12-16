from flask import Blueprint, request
from sqlalchemy import exc
from gtmd.app import db
from gtmd.models.Book import Book
from gtmd.models.Store import Store
from gtmd.models.User import User
from gtmd.tokenMethods import *
import json
seller_bp = Blueprint("seller", __name__, url_prefix="/seller")


@seller_bp.route("/create_store", methods=["GET", "POST"])
def create_store():
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
        return jsonify({"message": "商铺ID已存在"}), 401


@seller_bp.route("/add_book", methods=["GET", "POST"])
def add_book():
    token = jwtDecoding(request.headers.get("token"))
    seller_id = request.json.get("user_id")
    store_id = request.json.get("store_id")
    book_info = request.json.get("book_info")
    stock_level = request.json.get("stock_level")
    if token is None or token.json.get("user_id") != seller_id:
        return jsonify({"message": "卖家用户ID不存在"}), 501
    store = Store.query.filter_by(seller_id=seller_id, store_id=store_id).first()
    if store is None:
        return jsonify({"message": "商铺ID不存在"}), 502
    book = Book.query.filter_by(store_id=store_id, book_id=book_info['id']).first()
    if book is not None:
        return jsonify({"message": "图书ID已存在"}), 503
    book = Book(
        book_id=book_info["id"],
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
    db.session.commit()
    return jsonify({"message": "ok"}), 200


@seller_bp.route("add_stock_level", methods=["GET", "POST"])
def update_stock_level():
    token = jwtDecoding(request.headers.get("token"))
    seller_id = request.json.get("user_id")
    store_id = request.json.get("store_id")
    book_id = request.json.get("book_id")
    add_stock_level = request.json.get("add_stock_level")
    if token is None or token.json.get("user_id") != seller_id:
        return jsonify({"message": "卖家用户ID不存在"}), 501
    store = Store.query.filter_by(seller_id=seller_id, store_id=store_id).first()
    if store is None:
        return jsonify({"message": "商铺ID不存在"}), 501
    book = Book.query.filter_by(store_id=store_id, book_id=book_id).first()
    if book is None:
        return jsonify({"message": "图书ID不存在"}), 502
    book.stock_level += add_stock_level
    db.session.commit()
    return jsonify({"message": "ok"}), 200

