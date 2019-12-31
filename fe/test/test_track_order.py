import pytest
from fe.access.book import Book
from fe.access.new_buyer import register_new_buyer
from fe.access.new_function import *
import uuid
from fe.test.gen_book_data import GenBook


class TestTrackOrder:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):

        self.buyer_id = "test_track_order_buyer_id_{}".format(str(uuid.uuid1()))
        # 创建用户
        self.buyer_password = self.buyer_id
        self.buyer = register_new_buyer(self.buyer_id, self.buyer_password)

        # 生成十家不同店铺的订单
        for i in range(10):
            self.seller_id = "test_change_status_to_unreceived_seller_id_{}".format(str(uuid.uuid1()))
            self.store_id = "test_change_status_to_unreceived_store_id_{}".format(str(uuid.uuid1()))
            self.seller_password = self.seller_id
            # 创建商家用户并插入图书数据
            gen_book = GenBook(self.seller_id, self.store_id)
            ok, buy_book_id_list = gen_book.gen(non_exist_book_id=False, low_stock_level=False, max_book_count=20)
            self.buy_book_info_list = gen_book.buy_book_info_list
            assert ok

            # 生成订单
            code, self.order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
            assert code == 200

            self.total_price = 0
            for item in self.buy_book_info_list:
                book: Book = item[0]
                num = item[1]
                self.total_price = self.total_price + book.price * num

            code = self.buyer.add_funds(100 + self.total_price)
            assert code == 200

            if i % 5 == 0:
                code = cancel_order(self.buyer_id, self.buyer_password, self.order_id)
                assert code == 200
            else:
                if i % 5 >= 2:
                    code = self.buyer.payment(self.order_id)
                    assert code == 200
                if i % 5 >= 3:
                    code = change_unreceived(self.seller_id, self.seller_password, self.store_id, self.order_id)
                    assert code == 200
                if i % 5 >= 4:
                    code = change_received(self.buyer_id, self.buyer_password, self.order_id)
                    assert code == 200

    def test_ok(self):
        code = track_order(self.buyer_id, self.buyer_password)
        assert code == 200

    def test_error_user_id(self):
        code = track_order(self.buyer_id + "_x", self.buyer_password)
        assert code != 200

    def test_error_password(self):
        code = track_order(self.buyer_id, self.buyer_password + "_x")
        assert code != 200