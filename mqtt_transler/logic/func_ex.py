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
from collections import deque
from datetime import datetime, timedelta

# #########################  卡丁车  ########################
from decimal import Decimal
from queue import Queue

import settings
from db import db_car
from db.db_in_coin import db_insert_coin, db_send_coin
from my_mqtt.my_tools import print_db


class CarInfo(object):
    def __init__(self, cid, order, circle, sql_queue, send_func):
        self._cid = cid
        self._order = order
        self._circle = int(circle)
        self._sql_queue = sql_queue
        self._send_func = send_func
        self._cross_time = [datetime.now()]     # + timedelta(seconds=-10)

    def update_last_record(self):
        bt, et, cal = self._cross_time[-2], self._cross_time[-1], len(self._cross_time) - 1
        tt = Decimal((et - bt).total_seconds()).quantize(Decimal('0.00'))
        print(f'订单：{self._order}， 第{cal}/{self._circle}圈， 用时：{tt}')

        # 每圈用时写入数据库
        self._sql_queue.put((self._order, cal, bt, et, tt))

    def cross_and_over(self):
        '''
        put update to sql queue each circle, at the same time send a signal to counter.
        if finish all circles, stop the car
        :return: True: the Caller should remove this Element from it dict(), else False
        '''

        if True:
            self._cross_time.append(datetime.now())
            self.update_last_record()

            # 每完成一圈，给计数器加一，供电1秒
            self._send_func(f'{settings.TOPIC_ROOT_H}{self._cid}/{settings.TP_DRVO}', '1,1000,1')

            # 达到预定圈数，关闭继电器
            if len(self._cross_time) > self._circle:
                self._send_func(f'{settings.TOPIC_ROOT_H}{self._cid}/{settings.TP_RELAY}', 's,0,0')
                return True
        return False

    def force_stop(self):
        # 记录当前停止圈
        now = datetime.now()
        self._cross_time.append(now)
        self.update_last_record()

        # 记录剩余圈，全0
        while len(self._cross_time) <= self._circle:
            self._cross_time.append(now)
            self.update_last_record()

        pass


class KDCarManager(object):

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

        if circle:      # 大于0，计圈
            # 保持 client_id 记录
            cls._all_cars[client_id] = CarInfo(client_id, order, circle, cls._sql_str, cls._send_mqtt_cmd_func)

            # 计数器清零，等测试（或放在开车时）
            cls._send_mqtt_cmd_func(f'{settings.TOPIC_ROOT_H}{client_id}/{settings.TP_DRVO}', '6,1000,1')  # 计数器清零
            # 一直通电
            return cls._send_mqtt_cmd_func(f'{settings.TOPIC_ROOT_H}{client_id}/{settings.TP_RELAY}', f's,-1,{circle}')

        elif _time:     # 计时
            return cls._send_mqtt_cmd_func(f'{settings.TOPIC_ROOT_H}{client_id}/{settings.TP_RELAY}', f's,{_time},0')
        else:           # 都为0，强制停车
            cls.force_stop(client_id)
            return cls._send_mqtt_cmd_func(f'{settings.TOPIC_ROOT_H}{client_id}/{settings.TP_RELAY}', f's,0,0')

    @classmethod
    def start_race(cls, cars: dict, circle: int):
        ls = []
        for k, v in cars.items():
            ls.extend(cls.start_single(k, v, circle, 0))    # extend, not append
        return ls

    def cross(self, cid):
        car = self._all_cars.get(cid)
        if car and car.cross_and_over():
            print(f'{cid} stop!')
            self._all_cars.pop(cid)

    @classmethod
    def force_stop(cls, cid):
        car = cls._all_cars.get(cid)
        if car:
            car.force_stop()
            cls._all_cars.pop(cid)

    @classmethod
    def update(cls):
        while True:
            time.sleep(0.01)
            if not cls._sql_str.empty():
                print_db('want to update sql')
                db_car.update(*cls._sql_str.get())


kd_car_mgr = KDCarManager()


# #########################  投币器  ########################

class InCoinDelayInfo(object):
    delay_time = 5      # 延时时间

    def __init__(self):
        self.total = 0
        self._remain = 0
        self.last_time = datetime.now()

    def add(self, coin):
        self.total += coin
        self._remain += coin
        self.last_time = datetime.now()

    def outed(self, coin):
        if self._remain > 0:
            self._remain -= coin
            print('icdi out')
            return True
        return False

    def get(self):
        # 未够时间返回0，够时间返回总数
        dur = (datetime.now() - self.last_time).total_seconds()
        if dur >= self.delay_time:
            return self.total
        return 0


class SendCoinChecking(object):
    check_time = 5     # 到时间就检测，如果没有退完，就提示剩余退币数

    def __init__(self):
        self.total = 0
        self._remain = 0
        self.order_queue = Queue()
        self.cur_order_coin = None
        self.last_time = datetime.now()

    def pop_order(self):
        tmp = self.cur_order_coin
        self.cur_order_coin = None if self.order_queue.empty() else self.order_queue.get()
        if self.cur_order_coin:
            self.total = self._remain = self.cur_order_coin[1]
            print(f'pop order: {self.cur_order_coin[0]}, want: {self.total}, remain: {self._remain}')
        return tmp

    def send(self, coin, order):
        if self.cur_order_coin:
            self.order_queue.put((order, coin))
        else:
            self.cur_order_coin = (order, coin)
            self.total = coin
            self._remain = coin

        print(f'order:{order} send coin: {coin}, remain: {self._remain}/{self.total}')
        self.last_time = datetime.now()

    def outed(self, coin):
        self._remain -= coin
        self.last_time = datetime.now()
        print(f'out coin: {coin}, remain: {self._remain}/{self.total}')
        return self._remain <= 0

    def remain(self):
        # 未够时间返回0，够时间返回总数
        dur = (datetime.now() - self.last_time).total_seconds()
        return dur >= self.check_time, self._remain

    def flash(self):
        self.last_time = datetime.now()


class InCoinManager(object):
    coin_coming_all = dict()
    coin_outing_all = dict()        # { cid: SendCoinChecking }
    do_not_add_to_outing = dict()
    _send_mqtt_cmd_func = None
    lock = threading.Lock()

    def __init__(self):
        t = threading.Thread(target=self.update, name='in_coin_update')  # 名字没意义
        t.start()
        pass

    @classmethod
    def set_send_func(cls, func):
        cls._send_mqtt_cmd_func = func

    def insert_coin(self, client_id, coin):

        icdi = self.coin_coming_all.setdefault(client_id, InCoinDelayInfo())
        icdi.add(1)

        self.do_not_add_to_outing[client_id] = self.do_not_add_to_outing.setdefault(client_id, 0) + 1

        pass

    def send_coin(self, client_id, coin, order=None):
        self.lock.acquire()
        scc = self.coin_outing_all.setdefault(client_id, SendCoinChecking())
        scc.send(coin, order)
        self.lock.release()

    def outed(self, client_id, coin):
        icdi = self.coin_coming_all.get(client_id)
        scc = self.coin_outing_all.get(client_id)
        if not icdi or not icdi.outed(coin):
            if scc:
                self.lock.acquire()
                if scc.outed(coin):     # 记录数据库，一个订单已经兑完成
                    oc = scc.pop_order()
                    if oc:
                        order, coin = oc
                        db_send_coin.record(client_id, coin, coin, order)
                        print(f'{client_id}: {coin}/{coin}, order:{order} finish! ******')
                self.lock.release()
        elif scc:
            scc.flash()

    @classmethod
    def update(cls):
        while True:
            time.sleep(1)
            for cid in list(cls.coin_coming_all.keys()):
                icdi = cls.coin_coming_all.get(cid)
                coin = icdi.get()
                if coin > 0:
                    print(f'in coin count: {coin}')
                    # 投币记录，直接写数据库
                    db_insert_coin.insert(cid, coin)
                    cls.coin_coming_all.pop(cid)

            cls.lock.acquire()
            for cid in list(cls.coin_outing_all.keys()):
                scc = cls.coin_outing_all.get(cid)
                check, remain = scc.remain()
                if check:
                    oc = scc.pop_order()
                    if oc:
                        # Todo: 记录未退币，可能有误，只记录到数据库，不提示，用户出退数有误时人工查询
                        if remain > 0:
                            db_send_coin.record(cid, oc[1], oc[1]-remain, oc[0])
                            print(f'****** {cid}: {remain}/{oc[1]}, order:{oc[0]} outing coin remained! ******')
                    else:
                        print(f'all finish!')
                        cls.coin_outing_all.pop(cid)
                pass
            cls.lock.release()


in_coin_mgr = InCoinManager()


# #########################  兑币机  ########################


class OutCoinManager(object):
    # Todo: 板子功能不足以兑币，暂无
    pass


out_coin_mgr = OutCoinManager()
