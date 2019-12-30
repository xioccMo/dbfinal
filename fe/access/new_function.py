import requests
from fe.access.auth import Auth


def change_unreceived(seller_id, password, store_id, order_id):
    json = {
        "user_id": seller_id,
        "store_id": store_id,
        "order_id": order_id
    }
    terminal = "CaiXukun"
    url = "http://127.0.0.1:5000/seller/change_unreceived"
    auth = Auth("http://127.0.0.1:5000")
    code, token = auth.login(seller_id, password, terminal)
    headers = {"token": token}
    r = requests.post(url, headers=headers, json=json)
    return r.status_code


def change_received(buyer_id, password, order_id):
    json = {
        "user_id": buyer_id,
        "order_id": order_id
    }
    terminal = "CaiXukun"
    url = "http://127.0.0.1:5000/buyer/change_received"
    auth = Auth("http://127.0.0.1:5000")
    code, token = auth.login(buyer_id, password, terminal)
    headers = {"token": token}
    r = requests.post(url, headers=headers, json=json)
    return r.status_code


def cancel_order(buyer_id, password, order_id):
    json = {
        "user_id": buyer_id,
        "order_id": order_id
    }
    terminal = "CaiXukun"
    url = "http://127.0.0.1:5000/buyer/cancel_order"
    auth = Auth("http://127.0.0.1:5000")
    code, token = auth.login(buyer_id, password, terminal)
    headers = {"token": token}
    r = requests.post(url, headers=headers, json=json)
    return r.status_code


def track_order_by_order_id(buyer_id, password, order_id):
    json = {
        "user_id": buyer_id,
        "order_id": order_id
    }
    terminal = "CaiXukun"
    url = "http://127.0.0.1:5000/buyer/track_order_by_order_id"
    auth = Auth("http://127.0.0.1:5000")
    code, token = auth.login(buyer_id, password, terminal)
    headers = {"token": token}
    r = requests.post(url, headers=headers, json=json)
    return r.status_code, r.json().get("orderdetail")


def track_order(buyer_id, password):
    json = {
        "user_id": buyer_id,
    }
    terminal = "CaiXukun"
    url = "http://127.0.0.1:5000/buyer/track_order"
    auth = Auth("http://127.0.0.1:5000")
    code, token = auth.login(buyer_id, password, terminal)
    headers = {"token": token}
    r = requests.post(url, headers=headers, json=json)
    return r.status_code


def add_comment(buyer_id, password, orderdetail_id, star, content):
    json = {
        "user_id": buyer_id,
        "orderdetail_id": orderdetail_id,
        "star": star,
        "content": content
    }
    terminal = "CaiXukun"
    url = "http://127.0.0.1:5000/buyer/add_comment"
    auth = Auth("http://127.0.0.1:5000")
    code, token = auth.login(buyer_id, password, terminal)
    headers = {"token": token}
    r = requests.post(url, headers=headers, json=json)
    return r.status_code


def update_comment(buyer_id, password, orderdetail_id, content):
    json = {
        "user_id": buyer_id,
        "orderdetail_id": orderdetail_id,
        "content": content
    }
    terminal = "CaiXukun"
    url = "http://127.0.0.1:5000/buyer/update_comment"
    auth = Auth("http://127.0.0.1:5000")
    code, token = auth.login(buyer_id, password, terminal)
    headers = {"token": token}
    r = requests.post(url, headers=headers, json=json)
    return r.status_code
