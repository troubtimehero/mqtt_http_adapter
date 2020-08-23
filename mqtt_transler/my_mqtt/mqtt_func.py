# author:阿豪
# contact: cyhol@qq.com
# datetime:2020/8/14 0014 11:35
# software: PyCharm

"""
文件说明：

"""


from __future__ import print_function

import paho.mqtt.client as mqtt
from datetime import datetime
import time
import json

import settings
from my_mqtt.my_tools import time_hms, print_db
from logic.func_ex import kd_car


# #################################################################


mqtt_client: mqtt.Client = None
dict_on_publish = dict()


def read_cmd(payload):
    if payload:
        cmd = ''
        for i in range(len(payload)):
            cmd += chr(payload[i])
        return cmd.split(sep=',')
    return ''


def set_subscribe_list(topics: list):
    mqtt_client.subscribe([(settings.TOPIC_GID + settings.TOPIC_ROOT_C + topic, 1) for topic in topics])


# 当客户端收到来自服务器的ConnAck响应时的回调。也就是申请连接，服务器返回结果是否成功等
def on_connect(client, userdata, flags, rc):
    print(f"[连接结果] rc:{mqtt.connack_string(rc)}")


def on_disconnect(client, userdata, rc):
    print('on_disconnect:' + mqtt.connack_string(rc), client, userdata)


def on_subscribe(client, userdata, mid, granted_qos):
    print("on_subscribe: mid={} qos={}".format(mid, granted_qos))


# 当消息已经被发送给中间人，on_publish()回调将会被触发
def on_publish(client, userdata, mid):
    print_db("on_publish: mid:" + str(mid))
    dict_on_publish[mid] = 1


# 文档《OneNET-MQTT.docx》
def pub_data_type5(ds_id, data):
    payload = bytearray(len(data) + 1)
    payload[0:-1] = data.encode('ascii')
    payload[-1] = 0x00
    print_db(time_hms(), ' publish ==> topic={}   payload={}'.format(ds_id, payload))
    ret = mqtt_client.publish(topic=ds_id, payload=payload, qos=2, retain=True)
    dict_on_publish[ret] = 1
    return ret


# 从服务器接收发布消息时的回调。
def on_message(client, userdata, msg):
    print_db(f'msg [{time_hms()}] ==> {msg.topic} {msg.payload}')
    deal_with_message(msg.topic, msg.payload)

    # 响应MQTT服务商，必要操作，请勿修改
    if '$creq' in msg.topic:
        time.sleep(0.01)
        client.publish(topic=msg.topic, payload=msg.payload)
        print('PubAck to Server %s:%s' % (msg.topic, msg.payload))


_mid = 0


def deal_with_message(topic, payload):
    # Todo: 透传板子消息
    if settings.MQTT_JUST_PASS_THROUGH:
        send_java_through(topic, payload)
        return

    cmd = read_cmd(payload)     # cmd: [client_id, param1, param2...]
    global _mid
    print(f'{_mid}.', end='')
    _mid += 1

    # rs232: 为设备上传的rs232数据的16进制字符串，例如：83F5表示2个字节0x83,0xf5
    if settings.TP_RS232 in topic:
        pass

    # uart:为设备上传的uart(或RS485)数据的16进制字符串，例如：83F5表示2个字节0x83,0xf5
    elif settings.TP_UART in topic:
        b = bytes([int(cmd[1][i:i+2], base=16) for i, d in enumerate(cmd[1]) if i % 2 == 0])
        d = {'hex': cmd[1], 'str': b.decode('ascii')}
        send_java_uart(topic, cmd[0], d)

    # adc:为设备上传的adc数据(范围0~65535) 十进制字符串，例如：2300 。
    # 0代表0V，65535代表VREF电压，如果需要精确传感，需要用户算法进行定标修正
    elif settings.TP_ADC in topic:
        pass

    # dio:为设备上传的数字输入电平： chnum,level 。chnum表示通道号(0,1)，level表示电平(0,1)。
    # 当某个IO口电平发生变化时，模块会主动发送该消息
    # 分为DIOA,DIOB
    elif settings.TP_DIO in topic:
        # print('on_message_dio', cmd)
        if '1' == cmd[2]:
            kd_car.cross(cmd[0])

    # relay:为设备上传的继电器当前状态，status 。定义如下：
    #   0继电器当前处于断开状态
    #   -1 继电器将一直导通
    #   >0 继电器将导通多少秒
    # 当继电器断开或导通状态发生改变时，模块会主动发送该消息。
    # 板子重启时自动连通1秒，远程控制时也有通知，无需响应
    elif settings.TP_RELAY in topic:
        pass

    # board:
    # 功能1 ：为设备上电或重新连线时或主机给模块发送ping命令时发送的电路板信息：iccid,imei,csq,lac,cid    其中 csq为信号质量，lac,cid为基站信息，可用于定位
    # 功能2：mqtt转发器监测到从设备掉线时，mqtt转发器会给其它设备发送掉线消息：offline, 设备可以监测此topic的消息，如果为offline来判断哪个设备掉线
    elif settings.TP_BOARD in topic:
        pass


def mqtt_init(cid, username, pwd) -> mqtt.Client:
    # if not init_flag:
    global mqtt_client
    mqtt_client = mqtt.Client(cid)
    # 开启日志记录
    mqtt_client.enable_logger()
    # 设置回调函数
    mqtt_client.on_connect = on_connect
    mqtt_client.on_disconnect = on_disconnect
    mqtt_client.on_publish = on_publish
    mqtt_client.on_message = on_message
    mqtt_client.on_subscribe = on_subscribe
    # 设置账号密码
    mqtt_client.username_pw_set(username=username, password=pwd)
    # 连接服务器
    mqtt_client.connect(settings.SERVER_IP, int(settings.SERVER_PORT), keepalive=100)
    # 订阅需要的 topic
    set_subscribe_list(settings.CLIENT_TOPICS)
    mqtt_client.loop_start()
    # init_flag = True

    print('mqtt_client: ', mqtt_client)
    return mqtt_client


def send_mqtt_cmd(topic, cmd):
    return [pub_data_type5(topic, cmd)]


def send_java_through(topic, payload):
    # Todo: 接收的数据，如果不知道怎么处理，要发送到主服务器
    if topic or payload:
        print('send_java_through')
    pass


def send_java_uart(topic, cid, cmd_dict):

    if topic not in settings.JAVA_NEED_RESPONSE:
        return

    data = {
        'topic': topic,
        'client_id': cid,
        'data': cmd_dict,
        'time': datetime.now().timestamp()      # 时间戳，防止数据重发错误。主服务器接收一条消息后，保存该时间戳，再收到同一时间的就过滤。
    }
    data = json.dumps(data)
    print(data)
    # r = requests.post(settings.JAVA_IP, data=data, timeout=settings.JAVA_TIMEOUT)
    # print(r.json())


# 发布的消息，收到板子回复，就把它移除，超时未回复返回 False
def is_on_publish(mid, remove=True):
    if dict_on_publish.get(mid):
        if remove:
            dict_on_publish.pop(mid)
        return True
    return False


def remove_publish_mid(mid: list):
    for m in mid:
        if dict_on_publish.get(m):
            dict_on_publish.pop(m)


# mid 由 send_mqtt_cmd_ex()返回，为 int 或 list，要区分
def wait_for_publish(mid: list, second=1):
    count = 0
    while True:
        time.sleep(0.1)
        for m in mid[:]:
            if is_on_publish(m):
                mid.remove(m)
        if len(mid) <= 0:
            return True
        count += 1
        if count > second * 10:
            return False


FUNC_TYPE_THROUGH = ('through', '透传')
FUNC_TYPE_OUT_COIN = ('out_coin', '退币')
FUNC_TYPE_RELAY_ON = ('relay_on', '继电器常通')
FUNC_TYPE_RELAY_OFF = ('relay_off', '继电器常断')
FUNC_TYPE_RELAY_SECOND = ('relay_second', '继电器通N秒')
FUNC_TYPE_CAR_SINGLE = ('car_single', '卡丁车单人(payload={"order":"订单", "circle/time":"圈数/时间"})')  # {"order":"789", "circle":"12"}
FUNC_TYPE_CAR_MULTI = ('car_multi', '卡丁车多人赛(client_id: 圈数(0强制停止), payload:{ "id1":"订单号1","id2":"订单号2", ... })')

FUNC_TYPE = [FUNC_TYPE_THROUGH, FUNC_TYPE_OUT_COIN, FUNC_TYPE_RELAY_ON, FUNC_TYPE_RELAY_OFF, FUNC_TYPE_RELAY_SECOND, FUNC_TYPE_CAR_SINGLE, FUNC_TYPE_CAR_MULTI]


# 例如 /host/1010016346/relay
def make_topic(client_id, func):
    return f'{settings.TOPIC_ROOT_H}{client_id}/{func}'


def send_mqtt_cmd_ex(cmd_type, client_id, func, payload, no_check, password) -> (bool, list, str):
    print('send_mqtt_cmd_ex() enter')

    settings.CLIENT_IDS.add(client_id)
    print(settings.CLIENT_IDS)

    # ---------------- 透传 ----------------
    if cmd_type == FUNC_TYPE_THROUGH[0]:
        if func in settings.HOST_TOPICS or no_check:
            return True, send_mqtt_cmd(make_topic(client_id, func), payload), ''
        print('error topic')

    # ---------------- 退币 ----------------
    elif cmd_type == FUNC_TYPE_OUT_COIN[0]:
        if payload and payload.isnumeric() and int(payload) > 0:
            return True, send_mqtt_cmd(make_topic(client_id, settings.TP_RELAY), 's,-1,{}'.format(payload)), ''
        return False, -1, 'payload 为正整数'

    # ---------------- 继电器ON ----------------
    elif cmd_type == FUNC_TYPE_RELAY_ON[0]:
        return True, send_mqtt_cmd(make_topic(client_id, settings.TP_RELAY), 's,-1,0'), ''

    # ---------------- 继电器OFF ----------------
    elif cmd_type == FUNC_TYPE_RELAY_OFF[0]:
        return True, send_mqtt_cmd(make_topic(client_id, settings.TP_RELAY), 's,0,0'), ''

    # ---------------- 继电器通N秒 ----------------
    elif cmd_type == FUNC_TYPE_RELAY_SECOND[0]:
        if payload and payload.isnumeric() and int(payload) > 0:
            return True, send_mqtt_cmd(make_topic(client_id, settings.TP_RELAY), 's,{},0'.format(payload)), ''
        return False, -1, 'payload 为正整数'

    # ---------------- 卡丁车单人 ----------------
    elif cmd_type == FUNC_TYPE_CAR_SINGLE[0]:
        # noinspection PyBroadException
        try:
            info = json.loads(payload)
            order, circle, _time = info.get("order", None), info.get("circle", None), info.get("time", None)
            if not order or not (circle or _time):
                return False, -1, '参数不正确'
            if not order.isnumeric() or circle and not circle.isnumeric() or _time and not _time.isnumeric():
                print_db(f"order:{order} {order.isnumeric()}, circle:{circle} {circle.isnumeric()}")
                return False, -1, '订单号或圈数或时间错误'
            return True, kd_car.start_single(client_id, order, circle, _time), ''
        except Exception as err:
            return False, -1, err
        pass

    # ---------------- 卡丁车多人比赛 ----------------
    elif cmd_type == FUNC_TYPE_CAR_MULTI[0]:     #
        # noinspection PyBroadException
        try:
            cars_info = json.loads(payload)
            for k, v in cars_info.items():
                if not k.isnumeric() or not v.isnumeric():
                    return False, -1, '订单号或设备ID错误'
            return True, kd_car.start_race(cars_info, int(client_id)), ''
        except Exception as err:
            return False, -1, err

    else:
        print('error func_ex')
    return False, -1, '该指令无效，如果是新测试的function，请勾选“不验证”'


kd_car.set_send_func(send_mqtt_cmd)
