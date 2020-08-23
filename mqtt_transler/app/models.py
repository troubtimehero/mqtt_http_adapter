# author:阿豪
# contact: cyhol@qq.com
# datetime:2020/8/19 13:24
# software: PyCharm

"""
文件说明：

"""
from app import db


class ModelKaDingChe(db.Model):
    """
    卡丁车支付记录详情表（几圈几条记录）
    """

    __tablename__ = 'tz_zry_carrecord_detail'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)    # 主键
    record_id = db.Column(db.Integer)       # 消费记录ID
    create_time = db.Column(db.DateTime)        # 创建时间
    type = db.Column(db.Integer)            # 记录类型
    end_time = db.Column(db.DateTime)           # 结束时间
    r_begin_time = db.Column(db.DateTime)       # 实际开始
    r_end_time = db.Column(db.DateTime)         # 实际结束
    cal_num = db.Column(db.Integer)         # 计圈数
    cal_time = db.Column(db.DECIMAL(10, 2))     # 用时（分钟）
    status = db.Column(db.Integer)          # 订单状态 0未结束  1已结束

    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4'
    }

    def __repr__(self):
        return f'<id:{self.id}, record:{self.record_id}, create_time:{self.create_time}, cal_num:{self.cal_num}'
