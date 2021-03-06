import pytest

import random

from fe.access.book import Book
from fe.access.new_buyer import register_new_buyer
from fe.access.new_function import change_unreceived
import uuid

from fe.test.gen_book_data import GenBook


class TestChangeReceived:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_change_status_to_unreceived_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_change_status_to_unreceived_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_change_status_to_unreceived_buyer_id_{}".format(str(uuid.uuid1()))
        self.seller_password = self.seller_id
        self.buyer_password = self.buyer_id

        # 创建商家用户并插入图书数据
        gen_book = GenBook(self.seller_id, self.store_id)
        ok, buy_book_id_list = gen_book.gen(non_exist_book_id=False, low_stock_level=False, max_book_count=20)
        self.buy_book_info_list = gen_book.buy_book_info_list
        assert ok

        # 创建用户
        self.buyer = register_new_buyer(self.buyer_id, self.buyer_password)

        # 生成订单
        code, self.order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200

        self.total_price = 99
        for item in self.buy_book_info_list:
            book: Book = item[0]
            num = item[1]
            self.total_price = self.total_price + book.price * num

        # 充值金额
        code = self.buyer.add_funds(self.total_price)
        assert code == 200

        # 支付订单
        code = self.buyer.payment(self.order_id)
        assert code == 200

    def test_ok(self):
        # 先更改
        code = change_unreceived(self.seller_id, self.seller_password, self.store_id,  self.order_id)
        assert code == 200

    def test_seller_id_error(self):
        code = change_unreceived(self.seller_id + "_x", self.seller_password, self.store_id, self.order_id)
        assert code != 200

    def test_seller_password_error(self):
        code = change_unreceived(self.seller_id, self.seller_password + "_x", self.store_id,  self.order_id)
        assert code != 200

    def test_store_id_error(self):
        code = change_unreceived(self.seller_id, self.seller_password + "_x", self.store_id,  self.order_id)
        assert code != 200

    def test_order_id_error(self):
        code = change_unreceived(self.seller_id, self.seller_password, self.store_id, self.order_id + "_x")
        assert code != 200

    def test_repeat_change_status(self):
        code = change_unreceived(self.seller_id, self.seller_password, self.store_id, self.order_id)
        assert code == 200

        code = change_unreceived(self.seller_id, self.seller_password, self.store_id, self.order_id)
        assert code != 200
