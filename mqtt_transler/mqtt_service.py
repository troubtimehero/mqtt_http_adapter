# 从app模块中导入app应用
from main import main
import win32serviceutil
import win32service
import win32event
import winerror
import win32timezone    # 打包完执行是需要
import servicemanager
import sys
import os


class WinPollManager(win32serviceutil.ServiceFramework):
    """
    #1.安装服务
    python WinPollManager.py install

    #2.让服务自动启动
    python WinPollManager.py --startup auto install

    #3.启动服务
    python WinPollManager.py start

    #4.重启服务
    python WinPollManager.py restart

    #5.停止服务
    python WinPollManager.py stop

    #6.删除/卸载服务
    python WinPollManager.py remove
    """

    _svc_name_ = "mqtt_service"  # 服务名
    _svc_display_name_ = "mqtt_service"  # 服务在windows系统中显示的名称
    _svc_description_ = "python windows service for translate from http to mqtt"  # 服务的描述

    def __init__(self, args):
        print('init')
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.isAlive = True
        self._poll_intvl = 30

    def SvcDoRun(self):
        main()


    def SvcStop(self):
        print('stop')
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.isAlive = False


if __name__ == '__main__':
    if len(sys.argv) == 1:
        try:
            print(1)
            evtsrc_dll = os.path.abspath(servicemanager.__file__)
            servicemanager.PrepareToHostSingle(WinPollManager)
            servicemanager.Initialize('WinPollManager', evtsrc_dll)
            servicemanager.StartServiceCtrlDispatcher()
        except win32service.error as details:
            print(2)
            if details[0] == winerror.ERROR_FAILED_SERVICE_CONTROLLER_CONNECT:
                win32serviceutil.usage()
    else:
        print(3)
        win32serviceutil.HandleCommandLine(WinPollManager)  # 括号里参数可以改成其他名字，但是必须与class类名一致；


#
# # 防止被引用后执行，只有在当前模块中才可以使用
# if __name__ == '__main__':
#     print('参数个数为:', len(sys.argv), '个参数。')
#     print('参数列表:', str(sys.argv))
#
#     client = mqtt_init(cid=settings.DEV_ID, username=settings.PRO_ID, pwd=settings.AUTH_INFO)
#     print('connect finish!')
#
#     app.run(host=settings.HTTP_HOST, port=settings.HTTP_PORT)
#
#     print('run finish')
#
#     # 下面的 Tornado 方式不可并行访问
#     # s = HTTPServer(WSGIContainer(app))
#     # s.listen(9900)  # 监听 9900 端口
#     # IOLoop.current().start()
