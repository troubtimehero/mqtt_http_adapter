# author:阿豪
# contact: cyhol@qq.com
# datetime:2020/8/18 0018 16:30
# software: PyCharm

"""
文件说明：

"""

# from db.my_database import my_db
from datetime import datetime

from app.models import ModelInCoin, ModelSendCoin
from app import db


class DBInsertCoin(object):

    @staticmethod
    def select(cid):
        rec = ModelInCoin.query.filter_by(dev_id=cid).all()
        for r in rec:
            print(r.id, r.dev_id, r.in_count, r.create_time)

    @staticmethod
    def insert(cid, coin):
        c = ModelInCoin()
        c.dev_id = cid
        c.in_count = coin
        c.create_time = datetime.now()
        db.session.add(c)
        db.session.commit()


db_insert_coin = DBInsertCoin()


class DBSendCoin(object):

    @staticmethod
    def select(cid):
        rec = ModelSendCoin.query.filter_by(dev_id=cid).all()
        for r in rec:
            print(r.id, r.dev_id, r.want, r.got, r.record_id, r.create_time)

    @staticmethod
    def record(cid, want, got, order):
        sc = ModelSendCoin()
        sc.dev_id = cid
        sc.want = want
        sc.got = got
        sc.record_id = order
        sc.create_time = datetime.now()
        db.session.add(sc)
        db.session.commit()


db_send_coin = DBSendCoin()


