# -*- coding: utf-8 -*-
import argparse
from datetime import datetime, timedelta
import logging
from subprocess import Popen, PIPE
import threading
import time
from os.path import abspath, dirname, join, isfile
import pprint
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from util import config_from_pyfile

logging.basicConfig(level=logging.DEBUG)

DAYS = 15
CONFIG = {}
NO_REPORT = False


def alertSsl(hostname, delta):

    d = int(delta.total_seconds() / 86400)

    msg = "域名 %s 的SSL证书将在%s天内爆炸，请注意更新。"
    msg %= (hostname, d)
    logging.debug(msg)

    params = {
        'token': CONFIG['DINGTALK_TOKEN'],
        'message': msg,
    }

    # FIXME:
    url = 'http://example.com/...'

    qs = urlencode(params)
    url += '?' + qs

    req = Request(url)
    urlopen(req)


def runShellCommand(cmd):
    logging.debug('running cmd: %s' % cmd)
    p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = p.communicate()
    return p.returncode, stdout, stderr


tpl = """
timeout 5 openssl s_client -servername %s -connect %s:443 \
  -showcerts 2>/dev/null \
  < /dev/null  | openssl x509 -enddate -noout
"""


def checkSslHostname(servername, connect):
    command = tpl % (servername, connect)

    ex, stdout, stderr = runShellCommand(command)
    if ex == 0:
        s = stdout.decode('ascii').split('=')[1].strip()
        dt = datetime.strptime(s, '%b %d %H:%M:%S %Y %Z')
        logging.debug(dt)
        delta = (dt - datetime.now())
        logging.debug('delta: {}'.format(delta))
        if delta < timedelta(days=DAYS):
            return False, delta
    else:
        logging.error('%s 已爆炸' % servername)

    return True, None


def check():
    logging.info('>>>> start check ')
    for servername, connect in CONFIG['HOSTNAMES'].items():
        ok, delta = checkSslHostname(servername, connect)
        if not ok and (not NO_REPORT):
            alertSsl(servername, delta)

    logging.info('>>>> check done ')


def main():
    global CONFIG, DAYS, NO_REPORT
    ap = argparse.ArgumentParser()
    ap.add_argument('--interval-in-hour', type=int, default=24)
    ap.add_argument('--threshold-day', type=int, default=15)
    ap.add_argument('--no-report', action='store_true')

    options = ap.parse_args()
    interval = options.interval_in_hour
    if options.no_report:
        NO_REPORT = True

    # 加载根目录下的 config.py
    fn = abspath(join(abspath(dirname(__file__)), 'config.py'))
    CONFIG.update(config_from_pyfile(fn))

    # 加载根目录下的 config_local.py
    fn = abspath(join(abspath(dirname(__file__)), 'config_local.py'))
    if isfile(fn):
        CONFIG.update(config_from_pyfile(fn))

    pprint.pprint(CONFIG)

    DAYS = options.threshold_day

    while True:
        t = threading.Thread(target=check)
        t.start()
        time.sleep(3600 * interval)


if __name__ == '__main__':
    main()
