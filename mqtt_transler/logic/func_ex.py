# author:阿豪
# contact: cyhol@qq.com
# datetime:2020/8/17 0017 14:12
# software: PyCharm

"""
文件说明：功能扩展
1、卡丁车自动完成跑圈记数、录入数据库
"""
import threading
import time
from collections import namedtuple
from datetime import datetime, timedelta


# #########################  卡丁车  ########################
from decimal import Decimal
from queue import Queue

import settings
from db import db_kadingche
from my_mqtt.my_tools import print_db


class CarInfo(object):
    def __init__(self, cid, order, circle, sql_queue, send_func):
        self._cid = cid
        self._order = order
        self._circle = int(circle)
        self._sql_queue = sql_queue
        self._send_func = send_func
        self._cross_time = [datetime.now()]     # + timedelta(seconds=-10)

    def cross_and_over(self):
        # if self._cross_time[-1] + timedelta(seconds=0.5) < datetime.now():    # 卡丁车跑圈，收到光眼消息太快不计算，防止数据错乱
        if True:
            print_db(f'{self._cid} cross!')
            self._cross_time.append(datetime.now())
            # self._cross_time[0] += timedelta(seconds=10)

            bt, et, cal = self._cross_time[-2], self._cross_time[-1], len(self._cross_time)-1
            tt = Decimal((et - bt).total_seconds()).quantize(Decimal('0.00'))
            print(f'订单：{self._order}， 第{cal}/{self._circle}圈， 用时：{tt}')

            # 每圈用时写入数据库
            self._sql_queue.put((self._order, cal, bt, et, tt))
            print_db('put queue finish!')

            # 每完成一圈，给计数器加一，供电1秒
            self._send_func(f'{settings.TOPIC_ROOT_H}{self._cid}/{settings.TP_DRVO}', '1,1000,1')

            if cal >= self._circle:   # 达到预定圈数，关闭继电器
                print_db(f'want to stop {self._cid}')
                self._send_func(f'{settings.TOPIC_ROOT_H}{self._cid}/{settings.TP_RELAY}', 's,0,0')
                return True
        return False


class KDCar(object):

    _all_cars = dict()
    _sql_str = Queue()  # 保存数据库语句，用子线程执行
    _send_mqtt_cmd_func = None

    def __init__(self):
        t = threading.Thread(target=self.update, name='car_run_update')  # 名字没意义
        t.start()
        # t.join()
        pass

    @classmethod
    def set_send_func(cls, func):
        cls._send_mqtt_cmd_func = func

    @classmethod
    def start_single(cls, client_id, order, circle, _time):
        print_db(f'start: {client_id}, circle: {circle}, time: {_time}')

        if circle:
            cls._all_cars[client_id] = CarInfo(client_id, order, circle, cls._sql_str, cls._send_mqtt_cmd_func)

            # Todo: 开车，继电器通电，计数器清零，等测试（或放在开车时）
            cls._send_mqtt_cmd_func(f'{settings.TOPIC_ROOT_H}{client_id}/{settings.TP_DRVO}', '6,1000,1')   # 计数器清零
            return cls._send_mqtt_cmd_func(f'{settings.TOPIC_ROOT_H}{client_id}/{settings.TP_RELAY}', f's,-1,{circle}')
        else:
            return cls._send_mqtt_cmd_func(f'{settings.TOPIC_ROOT_H}{client_id}/{settings.TP_RELAY}', f's,{_time},0')

    @classmethod
    def start_race(cls, cars: dict, circle: int):
        ls = []
        for k, v in cars.items():
            ls.extend(cls.start_single(k, v, circle))
        return ls

    def cross(self, cid):
        car = self._all_cars.get(cid)
        if car and car.cross_and_over():
            print(f'{cid} stop!')
            self._all_cars.pop(cid)

    @classmethod
    def update(cls):
        while True:
            time.sleep(0.01)
            if not cls._sql_str.empty():
                print_db('want to update sql')
                db_kadingche.update(*cls._sql_str.get())


kd_car = KDCar()

