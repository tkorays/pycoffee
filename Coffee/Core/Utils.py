from datetime import datetime
import getpass
from Coffee.Core.Settings import DEF_CFG
import click
import random


def merge_datetime(base_dt, diff_kv):
    dt = {
        'year': base_dt.year,
        'month': base_dt.month,
        'day': base_dt.day,
        'hour': base_dt.hour,
        'minute': base_dt.minute,
        'second': base_dt.second,
        'millisecond': 0
    }
    for k, v in diff_kv.items():
        dt[k] = v
    return datetime(
        dt['year'],
        dt['month'],
        dt['day'],
        dt['hour'],
        dt['minute'],
        dt['second'],
        dt['millisecond']
    )


def get_local_user():
    my_name = DEF_CFG.local_user
    return my_name or getpass.getuser()


def LOGD(s):
    enable = False
    if enable:
        click.echo(s)


def randstr(length):
    return ''.join(random.sample('abcdefghijklmnopqrstuvwxyz01234567890', length))


def web_page_compare(title, url_a, url_b):
    from flask import Flask
    app = Flask(__name__)

    @app.route('/', methods=['GET'])
    def index():
        return f"""
    <!DOCTYPE html><html><head><meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1"><title>{title}</title></head>
    <body style="padding: 0; margin: 0;">
    <div>
    <div style="float: left;width: 50%;height: 100%; padding: 0px;margin: 0px;">
    <iframe src="{url_a}" frameborder="0" style="width:100%; min-height: 2000px;"></iframe>
    </div>
    <div style="float: right;margin-left: 0px;width: 50%;height: 100%;">
    <iframe src="{url_b}" frameborder="0" style="width:100%; min-height: 2000px;"></iframe>
    </div>
    </div>
    </body></html>
    """

    app.run(host='127.0.0.1', port=random.randint(5000, 65535), debug=False)
