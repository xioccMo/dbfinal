import datetime
import time
from sqlalchemy import Column, String, DATETIME, Integer, TEXT, ForeignKey, create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

# 创建对象的基类:
Base = declarative_base()


class Order(Base):
    __tablename__ = "order"
    order_id = Column(String, primary_key=True, index=True, nullable=False)
    # 用户id
    buyer_id = Column(String, index=True, nullable=False)
    # 商店id
    store_id = Column(String, index=True, nullable=False)
    # 创建时间
    createtime = Column(DATETIME, default=datetime.datetime.now, nullable=False)
    # 订单状态
    status = Column(String, nullable=False)
    orderdetails = relationship("Orderdetail", backref="Orderdetail")


class Orderdetail(Base):
    __tablename__ = "orderdetail"
    orderdetail_id = Column(String, primary_key=True, index=True, nullable=False)
    order_id = Column(String, ForeignKey("order.order_id"), index=True, nullable=False)
    book_id = Column(String, index=True, nullable=False)
    count = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    createtime = Column(DATETIME, nullable=True)
    star = Column(Integer, nullable=True)
    content = Column(TEXT, nullable=True)


# 定义User对象:
class Foruncommentorder(Base):
    # 表的名字:
    __tablename__ = 'Foruncommentorder'
    id = Column(String, primary_key=True, index=True, nullable=False, autoincrement=True)
    order_id = Column(String, ForeignKey("order.order_id"), index=True, nullable=False)
    # 表的结构:
    order = relationship("Order", backref="Order")


def uncommentMonitor():
    engine = create_engine('mysql+mysqlconnector://root:AICaiXukun@localhost:3306/gtmddatabase')

    # 创建DBSession类型:
    DBSession = sessionmaker(bind=engine)

    while True:
        session = DBSession()
        foruncommentorder = session.query(Foruncommentorder).order_by(Foruncommentorder.id).first()
        if foruncommentorder is None:
            session.close()
            time.sleep(10)
            continue
        sec = (datetime.datetime.now() - foruncommentorder.order.createtime).total_seconds()
        if sec < 10:
            time.sleep(10 - sec)
        for orderdetail in foruncommentorder.order.orderdetails:
            if orderdetail.status == "uncommented":
                orderdetail.status = "commented"
                orderdetail.createtime = datetime.datetime.now()
                orderdetail.star = 5
                orderdetail.content = "蔡徐坤比心般默认好评！"
        session.delete(foruncommentorder)
        session.commit()
