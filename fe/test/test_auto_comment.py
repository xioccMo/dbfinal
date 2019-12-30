import time

import pytest
from fe.access.book import Book
from fe.access.new_buyer import register_new_buyer
from fe.access.new_function import *
import uuid
from fe.test.gen_book_data import GenBook
import random


class TestTrackOrderByOrderId:
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

    def test_overtime_ok(self):
        self.total_price = 0
        for item in self.buy_book_info_list:
            book: Book = item[0]
            num = item[1]
            self.total_price = self.total_price + book.price * num
        code = self.buyer.add_funds(self.total_price)
        assert code == 200

        code = self.buyer.payment(self.order_id)
        assert code == 200

        code = change_unreceived(self.seller_id, self.seller_password, self.store_id, self.order_id)
        assert code == 200

        code = change_received(self.buyer_id, self.buyer_password, self.order_id)
        assert code == 200

        code, self.orderdetail = track_order_by_order_id(self.buyer_id, self.buyer_password, self.order_id)
        assert code == 200

        self.orderdetail_id = random.choice(self.orderdetail)['orderdetail_id']
        self.star = random.randint(1, 5)
        self.content = "蔡徐坤爱乔碧萝"

        time.sleep(10.01)
        code = add_comment(self.buyer_id, self.buyer_password, self.orderdetail_id, self.star, self.content)
        assert code != 200

        code = update_comment(self.buyer_id, self.buyer_password, self.orderdetail_id, self.content)
        assert code == 200

    def test_not_overtime_ok(self):
        self.total_price = 0
        for item in self.buy_book_info_list:
            book: Book = item[0]
            num = item[1]
            self.total_price = self.total_price + book.price * num
        code = self.buyer.add_funds(self.total_price)
        assert code == 200

        code = self.buyer.payment(self.order_id)
        assert code == 200

        code = change_unreceived(self.seller_id, self.seller_password, self.store_id, self.order_id)
        assert code == 200

        code = change_received(self.buyer_id, self.buyer_password, self.order_id)
        assert code == 200

        code, self.orderdetail = track_order_by_order_id(self.buyer_id, self.buyer_password, self.order_id)
        assert code == 200

        self.orderdetail_id = random.choice(self.orderdetail)['orderdetail_id']
        self.star = random.randint(1, 5)
        self.content = "蔡徐坤爱乔碧萝"

        time.sleep(5)

        code = update_comment(self.buyer_id, self.buyer_password, self.orderdetail_id, self.content)
        assert code != 200

        code = add_comment(self.buyer_id, self.buyer_password, self.orderdetail_id, self.star, self.content)
        assert code == 200
