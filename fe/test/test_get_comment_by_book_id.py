import random

import pytest

from fe.access.book import Book
from fe.access.new_buyer import register_new_buyer
from fe.access.new_function import *

from fe.access.new_seller import register_new_seller
from fe.access import book
import uuid


class TestTrackOrderByOrderId:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_add_books_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_add_books_store_id_{}".format(str(uuid.uuid1()))
        self.seller_password = self.seller_id

        self.seller = register_new_seller(self.seller_id, self.seller_password)

        self.seller.create_store(self.store_id)

        book_db = book.BookDB()
        self.books = book_db.get_book_info(0, 5)
        self.book_id_list = []
        self.book_info_list = []

        for bk in self.books:
            code = self.seller.add_book(self.store_id, 0, bk)
            assert code == 200
            code = self.seller.add_stock_level(self.seller_id, self.store_id, bk.id, 100000)
            assert code == 200
            num = random.randint(1, 100)
            self.book_id_list.append((bk.id, num))
            self.book_info_list.append((bk, num))

        for i in range(10):
            self.buyer_id = "test_change_status_to_unreceived_buyer_id_{}".format(str(uuid.uuid1()))
            self.buyer_password = self.buyer_id
            self.buyer = register_new_buyer(self.buyer_id, self.buyer_password)

            # 生成订单
            code, self.order_id = self.buyer.new_order(self.store_id, self.book_id_list)
            assert code == 200

            self.total_price = 0
            for item in self.book_info_list:
                bk: Book = item[0]
                num = item[1]
                self.total_price = self.total_price + bk.price * num
            code = self.buyer.add_funds(self.total_price)
            assert code == 200

            code = self.buyer.payment(self.order_id)
            assert code == 200

            code = change_unreceived(self.seller_id, self.seller_password, self.store_id, self.order_id)
            assert code == 200

            code = change_received(self.buyer_id, self.buyer_password, self.order_id)
            assert code == 200

            code, self.orderdetails = track_order_by_order_id(self.buyer_id, self.buyer_password, self.order_id)
            assert code == 200
            for orderdeatail in self.orderdetails:
                orderdetail_id = orderdeatail['orderdetail_id']
                self.star = random.randint(1, 5)
                self.content = ""
                for j in range(random.randint(2, 5)):
                    self.content += chr(random.randint(0x4e00, 0x9fbf))
                code = add_comment(self.buyer_id, self.buyer_password, orderdetail_id, self.star, self.content)
                assert code == 200

    def test_ok(self):
        code = get_comment_by_book_id(self.store_id, random.choice(self.book_id_list)[0])
        assert code == 200

    def test_error_book_id(self):
        code = get_comment_by_book_id(self.store_id, random.choice(self.book_id_list)[0] + "_x")
        assert code != 200

    def test_error_store_id(self):
        code = get_comment_by_book_id(self.store_id + "_x", random.choice(self.book_id_list)[0] + "_x")
        assert code != 200