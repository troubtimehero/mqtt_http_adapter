import logging
from datetime import datetime
import configparser
import json
import os
import settings

logging.basicConfig(level=logging.INFO, filename='../exception.log')


def time_hms():
    return datetime.now().strftime('%m%d %H:%M:%S')


def log_err(err):
    # 这是记录到本地
    logging.info('[{}] {}'.format(time_hms(), err))

    # Todo: 应该记录到数据库
    pass


def print_db(*args):
    if settings.DEBUG_PRINT:
        print(*args)


def str_to_tm(data):
    # noinspection PyBroadException
    try:
        data = json.loads(data)
        return data['topic'], data['cmd']
    except Exception as result:
        log_err('{}  -> json.loads() error data [{}]'.format(result, data))
    return '', ''


def tm_to_str(topic, cmd):
    data = {
        'topic': topic,
        'cmd': cmd
    }
    return json.dumps(data)


def init_from_ini(keys):

    config = configparser.ConfigParser()
    config.read(settings.OUTSIDE_CONFIG_INI)
    for key in keys:
        s = getattr(settings, key)
        if not s:
            continue
        # noinspection PyBroadException
        try:
            v = config.get('settings', key)
            setattr(settings, key, v)
            print_db(f'LOAD SETTING: <{key}> {s} ==> ', end='')
            print_db(getattr(settings, key))

            # 特殊
            if key == 'DATABASE_ADDRESS':
                settings.Config.SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + getattr(settings, key)

        except Exception:
            pass


def init_from_json(keys):
    j = {}
    # noinspection PyBroadException
    try:
        with open(settings.OUTSIDE_CONFIG_JSON) as f:
            j.update(json.load(f))
    except Exception:
        pass

    for k in keys:
        if getattr(settings, k) and k in j.keys():
            print(f'LOAD SETTING: <{k}> {getattr(settings, k)} ==> ', end='')
            setattr(settings, k, j.get(k))
            print(getattr(settings, k))
