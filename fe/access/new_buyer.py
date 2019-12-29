from fe import conf
from fe.access import buyer, auth


# 注册新的买家
def register_new_buyer(user_id, password) -> buyer.Buyer:
    a = auth.Auth(conf.URL)
    code = a.register(user_id, password)
    assert code == 200
    s = buyer.Buyer(conf.URL, user_id, password)
    return s
