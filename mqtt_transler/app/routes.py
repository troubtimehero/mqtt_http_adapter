# author:阿豪
# contact: cyhol@qq.com
# datetime:2020/8/14 0014 11:12
# software: PyCharm

"""
文件说明：

"""
# 从app模块中即从__init__.py中导入创建的app应用
import json
import time

from app import app
from flask import request, render_template, url_for, redirect

from app.forms import SendCommandField
from my_mqtt.mqtt_func import wait_for_publish, on_http_post, mqtt_set_id_group
import settings
from my_mqtt.my_tools import log_err, print_db, get_last_n_lines
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
            return render_template('mqtt2.html', form=form)
    except Exception as err:
        log_err(err)
        return err.__str__()

    res = ''
    if form.validate_on_submit():
        cmd_type = request.form.get('cmd_type')
        client_id = request.form.get('client_id')
        func = request.form.get('func')
        payload = request.form.get('payload')
        no_check = request.form.get('no_check')
        password = request.form.get('password')

        print_db('cmd_type:', cmd_type, 'client_id:', client_id, 'func:', func, 'payload:', payload, 'no_check:', no_check, 'password:', password)

        can_send, mid, err = on_http_post(cmd_type, client_id, func, payload, no_check)
        if can_send:
            res = 'success' if wait_for_publish(mid) else 'timeout'
        else:
            res = err.__str__()
    else:
        res = "参数有误或者不完整"

    print_db('res:', res)
    # return render_template('mqtt2.html', string=res)
    return res


@app.route('/mqtt/init', methods=['GET', 'POST'])
def init():
    if request.method == 'GET':
        return json.dumps({'client_id': list(settings.CLIENT_IDS), 'count': len(settings.CLIENT_IDS)})

    # ======================================== 更新IP =============
    ip = request.form.get('ip')
    if ip:
        settings.JAVA_IP = ip

    # ======================================== 更新设备ID（旧） ============= id1,id2,id3,id4,id5,id6...
    client_ids = request.form.get('client_id')
    if client_ids:
        clean = request.form.get('clean')
        client_ids = request.form.get('client_id')
        ls = [x.strip() for x in client_ids.split(',')]
        settings.CLIENT_IDS = set() if clean == 'y' else set(settings.CLIENT_IDS)
        for cid in ls:
            settings.CLIENT_IDS.add(cid)
        with open(settings.OUTSIDE_CONFIG_CLIENT_IDS, 'w') as f:
            f.write(','.join(settings.CLIENT_IDS))

    return 'success'


# version=1.1
@app.route('/mqtt/init2', methods=['GET', 'POST'])
def init2():
    if request.method == 'GET':
        d = {
            'type': dict([(name, member.value) for name, member in settings.DevType.__members__.items()]),
            'ids': settings.CLIENT_IDS_GROUP
        }
        return json.dumps(d)

    # ======================================== 更新设备ID组 ============= 0=id1,id2&1=id3,id4&2=id5,id6
    clean = request.form.get('clean')
    client_ids_group = request.form.get('client_id_group')
    if client_ids_group:
        print(settings.CLIENT_IDS_GROUP)

        if clean:
            settings.CLIENT_IDS_GROUP.clear()

        groups = [g.strip() for g in client_ids_group.split('&')]
        is_changed = False

        for group in groups:
            try:
                group_type, ids_in_group = group.split('=')
                group_type = int(group_type)
                settings.CLIENT_IDS_GROUP.setdefault(group_type, [])
                # Todo: id分类
                ls = [x.strip() for x in ids_in_group.split(',')]

                # settings.CLIENT_IDS_GROUP[group_type] = [] if clean == 'y' else settings.CLIENT_IDS_GROUP[group_type]
                for cid in ls:
                    settings.CLIENT_IDS_GROUP[group_type].append(cid)
                    mqtt_set_id_group(cid, group_type)
                    time.sleep(0.02)
                    is_changed = True
            except IndexError or ValueError as err:
                log_err(f'upload client_id error: {group} ==> {err.__str__()}')
                continue

        if is_changed:
            print(settings.CLIENT_IDS_GROUP)
            new_groups = [f'{k}={",".join(v)}' for k, v in settings.CLIENT_IDS_GROUP.items()]
            with open(settings.OUTSIDE_CONFIG_CLIENT_IDS_GROUP, 'w') as f:
                f.write('&'.join(new_groups))

        settings.update_client_ids_dict()

    return 'success'


# 打包成系统服务，启动Windows服务时，表单不可用，只能直接POST
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

        if password != get_md5_hex([cmd_type, client_id, func, payload, no_check]):
            return 'password error'

        print(password)
        can_send, mid, err = on_http_post(cmd_type, client_id, func, payload, no_check)
        if can_send:
            res = 'success' if wait_for_publish(mid) else 'timeout'
        else:
            log_err(err)
            res = err

        print_db('res:', res)
    except Exception as err:
        log_err(err)
        res = err
    return res if res else 'unknown error'


def get_md5_hex(msg: list) -> str:
    h = hmac.new(settings.Config.SECRET_KEY.encode('utf-8'), b'', digestmod='MD5')  # 传入都是二进制

    for m in msg:
        if m:
            h.update(m.encode('utf-8'))

    return h.hexdigest()


@app.route('/mqtt/err/<count>', methods=['GET'])
def log_err_html(count):
    return get_log_html(settings.ACTIVATE_ERROR_LOG, count)


@app.route('/mqtt/info/<count>', methods=['GET'])
def log_info_html(count):
    return get_log_html(settings.ACTIVATE_INFO_LOG, count)


def get_log_html(file, count):
    if count.isnumeric():
        res = '''
    <html>
    <head>
        <title>Home Page - Microblog</title>
    </head>
    <body>'''
        for line in get_last_n_lines(file, int(count)):
            try:
                res += f'<p>{line.decode("utf-8")}</p>\n'
            except UnicodeDecodeError:
                res += f'<p>{line.decode("GBK")}</p>\n'
            except Exception:
                continue
        # res = '\n'.join([line.decode('utf-8') for line in get_last_n_lines(settings.ACTIVATE_INFO_LOG, int(count))])

        res += '''    </body>
        </html>
            '''

        return res

    return '<h1 style="color:#FF0000">请输入数字</h1>'


