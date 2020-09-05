# author:阿豪
# contact: cyhol@qq.com
# datetime:2020/8/24 16:25
# software: PyCharm

import os
import time
import logging
import inspect

'''
import inspect
def test():
    a = inspect.stack()[1]
    print a

得到一个元组，如：
(<frame object at 0x8604aa4>, 'test.py', 10, 'function_one', ['\t\tprint get_current_function_name()\n'], 0)

a = inspect.stack()[1]
该行代码所在函数（被调函数）栈幀是0，根据调用的顺序，这个调用链条上的函数栈幀偏移值递增1
a -> b -> c （a调用b,b调用c）c中通过inspect获得栈幀集合，对于c来说
函数b的栈幀是inspect.stack()[1],函数a的栈幀是inspect.stack()[2]



那么这个元组的分别是：(调用者的栈对象，调用者的文件名，调用行数，调用者函数名，调用代码，0)
最后的0未知其含义
'''


class Logger(object):

    @staticmethod
    def print_now():
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    def __init__(self):
        self.__logger = logging.getLogger()
        path = os.path.abspath("/tmp/TNLOG-error.log")
        handler = logging.FileHandler(path)
        self.__logger.addHandler(handler)
        self.__logger.setLevel(logging.NOTSET)

    def get_log_message(self, level, message):
        # message = "[%s] %s " %(self.printfNow(),message)

        frame, filename, line_no, function_name, code, unknown_field = inspect.stack()[2]
        '''日志格式：[时间] [类型] [记录代码] 信息'''
        return "[%s] [%s] [%s - %s - %s] %s" % (self.print_now(), level, filename, line_no, function_name, message)

    def info(self, message):
        message = self.get_log_message("info", message)
        self.__logger.info(message)

    def error(self, message):
        message = self.get_log_message("error", message)
        self.__logger.error(message)

    def warning(self, message):
        message = self.get_log_message("warning", message)
        self.__logger.warning(message)

    def debug(self, message):
        message = self.get_log_message("debug", message)
        self.__logger.debug(message)

    def critical(self, message):
        message = self.get_log_message("critical", message)
        self.__logger.critical(message)


logger = Logger()

if __name__ == "__main__":
    logger.info("hello")
