# 从app模块中导入app应用
import time

import settings
import sys
import getopt

from machine_encrypt.win_tips import tips_only
from my_mqtt.my_tools import init_from_json, init_from_ini, log_info, log_err, print_db
from machine_encrypt.activation import is_active
import ctypes


def main():

    # 未激活不可使用
    if not is_active(settings.ACTIVATE_CODE_FILE):
        return
    print('Activate success!')

    # ------------------- 从文件读取配置 -------------------
    if not init_from_json(settings.ENABLE_INIT_PARAMS):
        init_from_ini(settings.ENABLE_INIT_PARAMS)

    argv = sys.argv[1:]
    # ------------------- 从命令行读取配置 -------------------
    try:
        opts, args = getopt.getopt(argv, "d:p:a:m:j:")
    except getopt.GetoptError:
        opts = []
        pass

    for opt, arg in opts:
        # 设置本应用的 DEV_ID, PRO_ID, AUTH_INFO, (SERVER_IP = '183.230.40.39', SERVER_PORT = 6002)
        if opt == '-d':
            settings.DEV_ID = arg
        elif opt == '-p':
            settings.PRO_ID = arg
        elif opt == '-a':
            settings.AUTH_INFO = arg
        # 设置数据库  'root:abcdef@192.168.2.84:3306/tz_game?charset=utf8'
        elif opt == '-m':
            settings.Config.SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + arg
        # 设置Java服务器通讯地址  'http://127.0.0.1:8000/mqtt'
        elif opt == '-j':
            settings.JAVA_IP = arg

    # 不提供默认DIV_ID，设置好了才能使用
    if settings.DEV_ID == '' or settings.PRO_ID == '' or settings.AUTH_INFO == '':
        tips_only('《config.json》中必须设置“唯一的”\n DEV_ID:\n PRO_ID:\n AUTH_INFO:\n 三项，且不能与其他系统共用\n否则将造成连接异常', '配置提示')
        return

    # 加载，要放到配置之后
    from app import app
    from my_mqtt.mqtt_func import mqtt_init, mqtt_set_id_group

    # ------------------- 再从本地文档、数据库表 'tz_zry_car_relay' 读取 设备ID -------------------
    settings.CLIENT_IDS = settings.get_client_ids_from_database(settings.CLIENT_IDS)
    try:
        with open(settings.OUTSIDE_CONFIG_CLIENT_IDS) as f:
            ls = f.read().split(sep=',')
            for cid in ls:
                settings.CLIENT_IDS.add(cid.strip())
                print(f'Adding cid: {cid}')
            print(f'get {len(settings.CLIENT_IDS)} client_ids')
    except Exception:
        pass

    # Todo: 加载设备ID组
    # 先把Version1.0 的数据合并过来
    for cid in settings.CLIENT_IDS:
        settings.CLIENT_IDS_DICT[cid] = settings.DevType.DT_CAR.value
    # 再把Version1.1 加进来
    try:
        with open(settings.OUTSIDE_CONFIG_CLIENT_IDS_GROUP) as f:
            groups = f.read().split(sep='&')
            for group in groups:
                try:
                    group_type, ids_in_group = group.split('=')
                    group_type = int(group_type)
                    settings.CLIENT_IDS_GROUP.setdefault(group_type, [])
                    ls = [x.strip() for x in ids_in_group.split(',')]
                    for cid in ls:
                        settings.CLIENT_IDS_GROUP[group_type].append(cid)
                    print_db(f'get {group_type} : {settings.CLIENT_IDS_GROUP[group_type]}')
                except IndexError or ValueError or Exception as err:
                    log_err(f'init client_id error: {group} ==> {err.__str__()}')
                    continue

    except Exception:
        pass
    print('mqtt_main.py: ', settings.CLIENT_IDS_DICT)
    settings.update_client_ids_dict()
    print('mqtt_main.py: ', settings.CLIENT_IDS_DICT)
    pass

    # ------------------- 正式启动 -------------------
    client = mqtt_init(cid=settings.DEV_ID, username=settings.PRO_ID, pwd=settings.AUTH_INFO)
    print('connect finish!')
    # ------------------- 启动后才能设置设备功能 -------------------
    for cid, _type in settings.CLIENT_IDS_DICT.items():
        mqtt_set_id_group(cid, _type)
        time.sleep(0.02)
    log_info('启动成功')

    # ------------------- 隐藏窗口 -------------------
    whnd = ctypes.windll.kernel32.GetConsoleWindow()
    if whnd != 0:
        ctypes.windll.user32.ShowWindow(whnd, 0)
        ctypes.windll.kernel32.CloseHandle(whnd)

    app.run(host=settings.HTTP_HOST, port=settings.HTTP_PORT)

    print('run finish')


if __name__ == '__main__':
    main()
