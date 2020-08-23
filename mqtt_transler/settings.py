'''
本文件包含所有设置
'''

# 登录设置
import os


# True：所有指令不作处理，只做中介透传，由系统处理所有业务逻辑
# False：本应用负责处理一部分已规定的业务逻辑，未知指令直接忽略
MQTT_JUST_PASS_THROUGH = False

DEV_ID = "614972454"    # 设备ID
PRO_ID = "286221"       # 产品ID
AUTH_INFO = "10086"     # APIKEY

SERVER_IP = '183.230.40.39'
SERVER_PORT = 6002

# 需要订阅的主题
# 1、SDC00GZA板子规定，无需修改
# 2、如果板子升级更多功能，根据技术文档修改这里
TOPIC_GID = ''     # '/12581'  暂时不知道什么用，加入分组后测试，仍不需要 group_id
TOPIC_ROOT_C = '/client/'
TOPIC_ROOT_H = '/host/'

TP_RS232 = "rs232"
TP_UART = "uart"
TP_ADC = "adc"
TP_DIO = "dio"
TP_RELAY = "relay"
TP_BOARD = "board"

TP_DRVO = "drvo"   # host才有
TP_SET_RS232 = "rs232/settings"
TP_SET_UART = "uart/settings"
TP_ALL = "all"

CLIENT_TOPICS = [
    TP_RS232,
    TP_UART,
    TP_ADC,
    TP_DIO,
    TP_RELAY,
    TP_BOARD,
]

HOST_TOPICS = [
    TP_RS232,
    TP_SET_RS232,
    TP_UART,
    TP_SET_UART,
    TP_RELAY,
    TP_DRVO,
    TP_DIO,
    TP_ADC,
    TP_ALL,
]


# 需要订阅的设备，应根据每个场地实际的设备进行设置，或从数据库加载
CLIENT_IDS = [
    "1010016342",
    "1010016346",
    "1010016349",
    "1010016350",
]


# 把 list 转成 set
def get_client_ids_from_database(ls) -> set:
    ids = []
    # Todo: 从数据库加载本场地可用的 id，用于MQTT订阅，否则需要手动设置上面的 CLIENT_IDS

    ls = ids if ids else ls
    return set(ls)


# #########################  HTTP   ######################################

HTTP_HOST = '0.0.0.0'   # 同一台机器上访问用 None， 跨机器用 '0.0.0.0'
HTTP_PORT = 5000        # HTTP端口


# #########################  JAVA   ######################################

# 板子数据上传地址，POST方法，【端口必须与本应用不一样】
JAVA_IP = 'http://127.0.0.1:8000/mqtt'
# 发送到主服务器的数据超时时间
JAVA_TIMEOUT = 3
# 收到主服务器指令，转发到MQTT，MQTT立即返回，但不代表指定设备已经接收。如果需要知道设备状态，主服务器可以向本程序订阅。不需要的就不发给主服务器了，减轻负担
JAVA_NEED_RESPONSE = ['us232', 'uart', 'adc', 'dio', 'board']      # relay 应该是不需要的


# #########################   数据库  ######################################

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_ADDRESS = 'root:abcdef@192.168.2.84:3306/tz_game?charset=utf8'


class Config(object):
    # 为了确保表单提交过来的是安全的，所以我们设定一个安全钥匙。
    SECRET_KEY = 'ZRY!2020.08-10*9hjas53^#nm#BBJ*k23x['
    WTF_CSRF_ENABLED = False

    # 格式为mysql+pymysql://数据库用户名:密码@数据库地址:端口号/数据库的名字?数据库格式
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://'+DATABASE_ADDRESS
    # 如果你不打算使用mysql，使用这个连接sqlite也可以
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR,'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


# #########################   系统加密  ######################################

ACTIVATE_DIR = 'C:/mqtt'
ACTIVATE_CODE_FILE = 'C:/mqtt/zry.txt'
ACTIVATE_CODE_QRCODE = 'C:/mqtt/qrcode.png'


# #########################   配置文档  ######################################

OUTSIDE_CONFIG_INI = 'C:/mqtt/config.ini'
OUTSIDE_CONFIG_JSON = 'C:/mqtt/config.json'
OUTSIDE_CONFIG_CLIENT_IDS = 'C:/mqtt/client_id.ini'


# #########################   可配置项  ######################################

ENABLE_INIT_PARAMS = [
    'MQTT_JUST_PASS_THROUGH',
    'DEV_ID',
    'PRO_ID',
    'AUTH_INFO',
    'SERVER_IP',
    'SERVER_PORT',
    'CLIENT_TOPICS',
    'HOST_TOPICS',
    'CLIENT_IDS',
    'HTTP_HOST',
    'HTTP_PORT',
    'JAVA_IP',
    'JAVA_TIMEOUT',
    'JAVA_NEED_RESPONSE',
    'DATABASE_ADDRESS',
]


# #########################   调试  ######################################

DEBUG_PRINT = False
