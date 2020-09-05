from __future__ import print_function

from datetime import datetime
from multiprocessing import Queue
import time

import paho.mqtt.client as mqtt
import struct
import json

# CONNECT 方式：
# client_id:     DEV_ID
# username:  PRO_ID
# password:   AUTHINFO(鉴权信息)
# 可以连接上设备云，CONNECT 和 CONNACK握手成功
# temperature:已创建的一个数据流
#更多请查阅OneNet官方mqtt文档与paho-mqtt开发文档

#修改成自己的即可
DEV_ID = "617875162" #设备ID
PRO_ID = "286221" #产品ID
AUTH_INFO = "1008611"  #APIKEY


TYPE_JSON = 0x01
TYPE_FLOAT = 0x17

# #定义上传数据的json格式  该格式是oneNET规定好的  按格式修改其中变量即可
# body = {
#     "datastreams": [
#         {
#             "id": "616241300",  #对应OneNet的数据流名称
#             "relay": "s,100,0",
#         }
#     ]
# }


cmd_queue = Queue()


class MqttClient(mqtt.Client):
    def __init__(self, client_id, username, password):
        super().__init__(client_id)
        self.on_connect = self.my_on_connect
        self.on_disconnect = self.my_on_disconnect
        self.on_publish = self.my_on_publish
        self.on_message = self.my_on_message
        self.on_subscribe = self.my_on_subscribe
        self.username_pw_set(username=username, password=password)
        self.connect('183.230.40.39', port=6002, keepalive=100)

    @staticmethod
    def build_payload(type_, payload):
        datatype = type_
        packet = bytearray()
        packet.extend(struct.pack("!B", datatype))
        if isinstance(payload, str):
            u_data = payload.encode('utf-8')
            length = len(u_data)
            packet.extend(struct.pack("!H" + str(length) + "s", length, u_data))
        return packet

    # 当客户端收到来自服务器的CONNACK响应时的回调。也就是申请连接，服务器返回结果是否成功等
    @staticmethod
    def my_on_connect(client, userdata, flags, rc):
        print("连接结果:" + mqtt.connack_string(rc))
        #上传数据
        # json_body = json.dumps(body)
        # packet = build_payload(TYPE_JSON, json_body)
        # client.publish("$dp", packet, qos=1)  #qos代表服务质量

    @staticmethod
    def my_on_disconnect(client, userdata, rc):
        print('disconnect')

    # 从服务器接收发布消息时的回调。
    @staticmethod
    def my_on_message(client, userdata, msg):
        print('< on_message {} >'.format(datetime.now().strftime('%H:%M:%S')), end=' ')
        print(msg.topic + " ", msg.payload)
        time.sleep(0.5)
        if '$creq' in msg.topic:
            client.publish(topic=msg.topic, payload=msg.payload)
            print('publish %s:%s' % (msg.topic, msg.payload))

    @staticmethod
    def my_on_subscribe(client, userdata, mid, granted_qos):
        print("On Subscribed: qos = %d" % granted_qos)

    # 当消息已经被发送给中间人，on_publish()回调将会被触发
    @staticmethod
    def my_on_publish(self, client, userdata, mid):
        print("[on_publish] mid:" + str(mid), client, userdata)

    def pub_data_type3(self, ds_id, data):
        message = {
            ds_id: data,
            "data1": data,
            "data2": data,
            "data3": data,
            "data4": data,
            "data5": data,
            "data6": data,
        }
        message = json.dumps(message)
        mess_len = len(message)
        array = bytearray(mess_len + 3)
        array[0] = 3
        array[1] = int(mess_len / 256)
        array[2] = mess_len % 256
        array[3:] = message.encode('ascii')
        print(array)
        self.publish(topic='$dp', payload=array, qos=0)
        return array

    def pub_data_type1(self, ds_id, data):
        message = {
            'datastreams': [
                {
                    'id': ds_id,
                    'datapoints': [
                        {
                            'value': data
                        }
                    ]
                }
            ]
        }
        message = json.dumps(message)
        mess_len = len(message)
        array = bytearray(mess_len + 3)
        array[0] = 1
        array[1] = int(mess_len / 256)
        array[2] = mess_len % 256
        array[3:] = message.encode('ascii')
        print(array)
        self.publish(topic='$dp', payload=array, qos=0)

    @staticmethod
    def fill_bin(ds_id, data):
        mes1 = {"ds_id": ds_id}
        mes1 = json.dumps(mes1)
        payload = bytearray(len(mes1)+len(data)+7)
        payload[0] = 2      # type
        payload[1] = int(len(mes1) / 256)
        payload[2] = len(mes1) % 256
        payload[3:3+len(mes1)] = mes1.encode('ascii')
        payload[3 + len(mes1) + 0] = (len(data) >> 24) & 0xff
        payload[3 + len(mes1) + 1] = (len(data) >> 16) & 0xff
        payload[3 + len(mes1) + 2] = (len(data) >> 8) & 0xff
        payload[3 + len(mes1) + 3] = (len(data)) & 0xff
        payload[(len(mes1) + 7):] = data
        return payload


# 多进程中发布消息需要重新初始化mqttClient
def task(commands):
    count = 0
    while True:
        time.sleep(5)
        print('put task')
        commands.put(count)
        count += 1


def main():
    # 消息处理开启多进程
    # p = Process(target=task, args=(cmd_queue,))
    # p.start()

    client = MqttClient(client_id=DEV_ID, username=PRO_ID, password=AUTH_INFO)
    client.unsubscribe('/host/1010016346/relay')
    client.subscribe('/abc/123/hello', qos=0)
    client.loop_start()

    while True:
        time.sleep(3)
        if not client.is_connected():
            client.reconnect()
            print('reconnect')
            continue

        if not cmd_queue.empty():
            print('publish')
            client.pub_data_type1('temp', cmd_queue.get())


if __name__ == '__main__':
    main()
