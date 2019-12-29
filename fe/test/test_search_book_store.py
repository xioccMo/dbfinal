import pytest
from fe.access.book import Book
from fe.access.new_buyer import register_new_buyer
from fe.access.new_function import *
import uuid
from fe.test.gen_book_data import GenBook


class TestSearchBookInStore:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_change_status_to_unreceived_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_change_status_to_unreceived_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_change_status_to_unreceived_buyer_id_{}".format(str(uuid.uuid1()))
        self.seller_password = self.seller_id
        self.buyer_password = self.buyer_id
        self.key_word = "数据"

        # 创建商家用户并插入图书数据
        gen_book = GenBook(self.seller_id, self.store_id)
        ok, buy_book_id_list = gen_book.gen(non_exist_book_id=False, low_stock_level=False, max_book_count=20)
        self.buy_book_info_list = gen_book.buy_book_info_list
        assert ok

        # 创建用户
        self.buyer = register_new_buyer(self.buyer_id, self.buyer_password)

    def test_status_search_ok(self):
        code = search_book_store(self.buyer_id, self.buyer_password, self.store_id, self.key_word)
        assert code == 200

    def test_error_user_id(self):
        code = search_book_store(self.buyer_id + "_x", self.buyer_password, self.store_id, self.key_word)
        assert code != 200

    def test_error_password_id(self):
        code = search_book_store(self.buyer_id, self.buyer_password + "_x", self.store_id, self.key_word)
        assert code != 200
