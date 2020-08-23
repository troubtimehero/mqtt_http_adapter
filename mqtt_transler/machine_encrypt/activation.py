# author:阿豪
# contact: cyhol@qq.com
# datetime:2020/8/21 13:41
# software: PyCharm

"""
文件说明：
通过系统信息，生成加密文件，解密激活
"""
import hmac

from machine_encrypt.system_info import Win32Info
from machine_encrypt.win_tips import tips_create_code


# 压缩成更简单的字符串，方便人工操作
def get_short_system_info():
    data = Win32Info().collect_my_need()
    l = []

    h = hmac.new(b'zry.2020.lsh.0821', b'begin', digestmod='MD5')  # 传入都是二进制

    rams = data.setdefault('ram', [])
    for ram in rams:
        h.update(ram.setdefault('sn', 'FFFF').strip().encode('utf-8'))

    disks = data.setdefault('physical_disk_driver', [])
    for disk in disks:
        h.update(disk.setdefault('sn', 'FFFF').strip().encode('utf-8'))

    # 　160 bit (40位16进制)
    return h.hexdigest()


def create_active_code(info):
    ls = [ord(x) % 10 for x in info]
    ls = ''.join([str((ls[i] + ls[i+16]) % 10) for i in range(16)])
    return '-'.join([ls[i*4:(i+1)*4] for i in range(4)])


def is_active(filename):
    short_info = get_short_system_info()
    code = create_active_code(short_info)
    try:
        with open(filename) as f:
            line = f.readline()
            if line:
                if line == code:
                    return True
    except FileNotFoundError or Exception:
        pass

    if tips_create_code(short_info, code):
        with open(filename, 'w') as f:
            f.writelines([code])
            return True

    return False
