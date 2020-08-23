# author:阿豪
# contact: cyhol@qq.com
# datetime:2020/8/14 0014 11:12
# software: PyCharm

"""
文件说明：

"""
# 从app模块中即从__init__.py中导入创建的app应用
import json
from app import app
from flask import request, render_template, url_for, redirect

from app.forms import SendCommandField
from my_mqtt.mqtt_func import wait_for_publish, send_mqtt_cmd_ex
import settings
from my_mqtt.my_tools import log_err
import hmac


@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('mqtt'))


# 测试页面
@app.route('/mqtt2', methods=['GET', 'POST'])
def mqtt2():
    # noinspection PyBroadException
    try:
        form = SendCommandField()
        if request.method == 'GET':
            return render_template('mqtt.html', form=form)
    except Exception as err:
        return err

    res = ''
    if form.validate_on_submit():
        cmd_type = request.form.get('cmd_type')
        client_id = request.form.get('client_id')
        func = request.form.get('func')
        payload = request.form.get('payload')
        no_check = request.form.get('no_check')
        password = request.form.get('password')

        print('cmd_type:', cmd_type, 'client_id:', client_id, 'func:', func, 'payload:', payload, 'no_check:', no_check, 'password:', password)

        can_send, mid, err = send_mqtt_cmd_ex(cmd_type, client_id, func, payload, no_check, password)
        if can_send:
            res = 'success' if wait_for_publish(mid) else 'timeout'
        else:
            res = err
    else:
        res = "参数有误或者不完整"

    print('res:', res)
    # return render_template('mqtt.html', string=res)
    return res


@app.route('/mqtt/init', methods=['GET', 'POST'])
def init():
    if request.method == 'GET':
        return json.dumps({'client_id': list(settings.CLIENT_IDS), 'count': len(settings.CLIENT_IDS)})

    try:
        ip = request.form.get('ip')
        if ip:
            settings.JAVA_IP = ip

        clean = request.form.get('clean')
        client_ids = request.form.get('client_id')
        ls = [x.strip() for x in client_ids.split(',')]
        settings.CLIENT_IDS = set() if clean == 'y' else set(settings.CLIENT_IDS)
        for cid in ls:
            settings.CLIENT_IDS.add(cid)
        with open(settings.OUTSIDE_CONFIG_CLIENT_IDS, 'w') as f:
            f.write(','.join(settings.CLIENT_IDS))
    except Exception as err:
        return err

    return 'success'


# Todo: 打包成系统服务，启动Windows服务时，表单不可用，只能直接POST
@app.route('/mqtt', methods=['POST'])
def mqtt():
    # noinspection PyBroadException
    try:
        cmd_type = request.form.get('cmd_type')
        client_id = request.form.get('client_id')
        func = request.form.get('func')
        payload = request.form.get('payload')
        no_check = request.form.get('no_check')
        password = request.form.get('password')

        print('cmd_type:', cmd_type, 'client_id:', client_id, 'func:', func, 'payload:', payload, 'no_check:', no_check, 'password:', password)
        print('HEX：', get_md5_hex([cmd_type, client_id, func, payload, no_check]))
        if password != get_md5_hex([cmd_type, client_id, func, payload, no_check]):
            return 'password error'

        print(send_mqtt_cmd_ex)

        can_send, mid, err = send_mqtt_cmd_ex(cmd_type, client_id, func, payload, no_check, password)
        if can_send:
            res = 'success' if wait_for_publish(mid) else 'timeout'
        else:
            res = err

        print('res:', res)
        return res
    except Exception as err:
        log_err(err)


def get_md5_hex(msg: list) -> str:
    h = hmac.new(settings.Config.SECRET_KEY.encode('utf-8'), b'', digestmod='MD5')  # 传入都是二进制

    for m in msg:
        h.update(m.encode('utf-8'))

    return h.hexdigest()
