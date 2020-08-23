# author:阿豪
# contact: cyhol@qq.com
# datetime:2020/8/21 15:36
# software: PyCharm

"""
文件说明：

"""
import sys

import settings
from machine_encrypt.activation import create_active_code, get_short_system_info


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] in ['0', '1']:
        want = sys.argv[1]
    else:
        while True:
            print('0.生成激活码（非本机使用）\n1.生成激活码、并录入当前系统：')
            want = input()
            if want == '0' or want == '1':
                break

    if want == '1':     # 直接写入系统，不需要输入序列号
        code = create_active_code(get_short_system_info())
        with open(settings.ACTIVATE_CODE_FILE, 'w') as f:
            f.writelines([code])
            print(f'注册码：{code}\n已录入系统，可在 {settings.ACTIVATE_CODE_FILE} 查看')
            input()
    else:
        print('请输入32位序列号：')
        while True:
            try:
                code = create_active_code(input())
                print(f'注册码为：{code}')
                print(f'在待激活系统输入注册提示框，或写入 {settings.ACTIVATE_CODE_FILE} 第一行即可')
            except Exception:
                print('输入有误，请输入32位序列号')
                pass
