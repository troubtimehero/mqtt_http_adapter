# author:阿豪
# contact: cyhol@qq.com
# datetime:2020/8/21 15:13
# software: PyCharm

"""
文件说明：

"""
# from PIL import Image
import os

import qrcode
import easygui

import settings
from my_mqtt.my_tools import log_err


def tips_create_code(info, code):

    q = qrcode.main.QRCode()
    q.add_data(info)
    m = q.make_image()
    while True:
        try:
            m.save(settings.ACTIVATE_CODE_QRCODE)
            break
        except FileNotFoundError:
            os.mkdir(settings.ACTIVATE_DIR)
            with open(settings.ACTIVATE_CODE_QRCODE, 'w'):
                continue

    log_err(f'MQTT通讯模块未注册启动失败，序列号为：{info}')
    print(info)
    while True:
        box = easygui.enterbox(msg=f"MQTT通讯模块启动失败，请输入注册码后点 OK\n\n序列号：{info}",    # \n二维码已生成在：{settings.ACTIVATE_CODE_QRCODE}
                               title="未注册",
                               image=settings.ACTIVATE_CODE_QRCODE)
        if box is None:
            return False
        elif box == code:
            return True


def tips_only(msg, title):
    log_err(f'{title} : {msg}')
    easygui.msgbox(msg=msg, title=title, ok_button='OK')
