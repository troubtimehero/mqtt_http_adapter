import os
from datetime import datetime
import configparser
import json
import settings
import logging

# _logger = logging.getLogger('send_rec')
# _logger.addHandler(logging.StreamHandler(settings.ACTIVATE_INFO_LOG))
# _logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO, filename=settings.ACTIVATE_INFO_LOG)


def time_hms():
    return datetime.now().strftime('%m%d %H:%M:%S')


if not os.path.exists(settings.ACTIVATE_ERROR_LOG):
    with open(settings.ACTIVATE_ERROR_LOG, 'w') as f:
        pass


def log_err(msg):
    # 这是记录到本地
    with open(settings.ACTIVATE_ERROR_LOG, 'a') as f:
        msg = f'【{time_hms()}】 {msg.__str__()}\n'
        f.write(msg)

    # Todo: 应该记录到数据库
    pass

    return msg


def log_info(msg, *args):
    if settings.LOG_INFO:
        msg = f'【{time_hms()}】 {msg}'
        for a in args:
            msg += f' {a}'
        # _logger.info(msg)
        logging.info(msg)
    else:
        print(msg)
    return msg


def print_db(*args, **kwargs):
    if settings.DEBUG_PRINT:
        print(*args, **kwargs)


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
    '''填写需要读取的设置字段，放在项目目录《config.ini》中，只有 settings 段'''

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
            print_db(f'LOAD SETTING: <{key}> {s} ==> ', (getattr(settings, key)))

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

    got = False
    for k in keys:
        if getattr(settings, k) is not None and k in j.keys():
            print(f'LOAD SETTING: <{k}> {getattr(settings, k)} ==> ', end='')
            setattr(settings, k, j.get(k))
            print(getattr(settings, k))
            got = True
    return got


def get_last_n_lines(logfile, n):
    blk_size_max = 4096
    n_lines = []
    with open(logfile, 'rb') as fp:
        fp.seek(0, os.SEEK_END)
        cur_pos = fp.tell()
        while cur_pos > 0 and len(n_lines) < n:
            blk_size = min(blk_size_max, cur_pos)
            fp.seek(cur_pos - blk_size, os.SEEK_SET)
            blk_data = fp.read(blk_size)
            assert len(blk_data) == blk_size
            lines = blk_data.split('\n'.encode('utf-8'))

            # adjust cur_pos
            if len(lines) > 1 and len(lines[0]) > 0:
                n_lines[0:0] = lines[1:]
                cur_pos -= (blk_size - len(lines[0]))
            else:
                n_lines[0:0] = lines
                cur_pos -= blk_size

            fp.seek(cur_pos, os.SEEK_SET)

    if len(n_lines) > 0 and len(n_lines[-1]) == 0:
        del n_lines[-1]
    return n_lines[-n:]
