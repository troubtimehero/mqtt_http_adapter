# author:阿豪
# contact: cyhol@qq.com
# datetime:2020/8/18 0018 9:33
# software: PyCharm

"""
文件说明：
操作数据库
"""

# 导入pymysql模块
import pymysql

pymysql.install_as_MySQLdb()


class MyDatabase(object):

    def __init__(self, host, port, user, password, database, charset='utf8'):
        # 连接database
        self._conn = pymysql.connect(host=host, port=port, user=user, password=password, db=database, charset=charset)
        self._cursor = None

        # # 关闭数据库连接
        # conn.close()

    # def with_cursor(self, func):
    #     @functools.wraps(func)
    #     def wrapper(*args, **kw):
    #         self._cursor = self._conn.cursor()
    #         print('call %s():' % func.__name__)
    #         sql = func(*args, **kw)
    #         self._cursor.execute(sql)
    #         self._cursor.close()
    #     return wrapper

    # @with_cursor
    @staticmethod
    def select(sql):
        return 'select sql'

    @staticmethod
    def insert(tar, val, *args):
        return f'INSERT INTO {tar} VALUES(' + args.join(',') + ')'

    @staticmethod
    def update(tar, val, *args):
        return f'UPDATE '

    def execute(self, sql):
        with self._conn.cursor() as cursor:
            # noinspection PyBroadException
            try:
                print("sql execute: ", sql)
                res = cursor.execute(sql)
                return res, cursor.fetchall()
            except Exception as err:
                return -1, None


my_db = MyDatabase('192.168.2.84', 3306, 'root', 'abcdef', 'tz_game')
