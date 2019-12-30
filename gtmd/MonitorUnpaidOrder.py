import datetime
import time
from sqlalchemy import Column, String, DATETIME, ForeignKey, create_engine
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


# 定义User对象:
class Forunpaidorder(Base):
    # 表的名字:
    __tablename__ = 'Forunpaidorder'
    id = Column(String, primary_key=True, index=True, nullable=False, autoincrement=True)
    order_id = Column(String, ForeignKey("order.order_id"), index=True, nullable=False)
    # 表的结构:
    order = relationship("Order", backref="Order")


def unpaidMonitor():
    engine = create_engine('mysql+mysqlconnector://root:AICaiXukun@localhost:3306/gtmddatabase')

    # 创建DBSession类型:
    DBSession = sessionmaker(bind=engine)

    while True:
        session = DBSession()
        forunpaidorder = session.query(Forunpaidorder).order_by(Forunpaidorder.id).first()
        if forunpaidorder is None:
            session.close()
            time.sleep(10)
            continue
        sec = (datetime.datetime.now() - forunpaidorder.order.createtime).total_seconds()
        if sec < 10:
            time.sleep(10 - sec)
        if forunpaidorder.order.status == "unpaid":
            forunpaidorder.order.status = "canceled"
        session.delete(forunpaidorder)
        session.commit()