# author:阿豪
# contact: cyhol@qq.com
# datetime:2020/8/18 0018 16:30
# software: PyCharm

"""
文件说明：

"""

# from db.my_database import my_db
from app.models import ModelKaDingChe
from app import db


class DBKaDingChe(object):
    def __init__(self, table):
        self.table = table
        pass

    @staticmethod
    def select(order):
        print('db select enter')
        kdc = ModelKaDingChe.query.filter_by(record_id=order).all()
        for k in kdc:
            print(k.id, k.record_id, k.create_time, k.cal_num, k.cal_time)
        # sql = f'SELECT * FROM {self.table} WHERE RECORD_ID={order};'
        # my_db.execute(sql)

    @staticmethod
    def update(order, circle, begin_time, end_time, cal_time):
        k = ModelKaDingChe.query.filter_by(record_id=order, cal_num=circle).first()
        if k:
            k.r_begin_time = begin_time
            k.r_end_time = end_time
            k.cal_time = cal_time
            db.session.commit()
            print(f'{begin_time}, {end_time}, {cal_time}')
        else:
            print(f'[info] no sql record to update: record_id={order}, cal_num={circle}')
        pass


db_kadingche = DBKaDingChe('tz_zry_carrecord_detail')
