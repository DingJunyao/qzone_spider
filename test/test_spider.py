#!/usr/bin/env python3

"""An example of qzone_spider"""

import qzone_spider
from qzone_spider import db_control_mysql
from qzone_spider import svar
import logging
import time
import argparse

parser = argparse.ArgumentParser(description='manual to this script')
parser.add_argument('-u', type=str, default=None)
parser.add_argument('-p', type=str, default=None)
parser.add_argument('-q', type=int, default=20)
args = parser.parse_args()

QQ = args.u
password = args.p
quantity = args.q

if QQ is None and password is None:
    print('Usage: ./test-spider.py -u your_QQ_number -p your_password -q quantity')
    exit()


logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(name)s: %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

cookie, gtk, qzonetoken = qzone_spider.account_login(QQ, password)
end_order = 0
while end_order <= quantity:
    r_catch_time, end_order, rough_json = qzone_spider.get_rough_json('***REMOVED***', end_order, 20, 100, cookie, gtk, qzonetoken)
    if r_catch_time == 0 and end_order == -1:
        break
    end_order += 1
    for i in range(len(rough_json)):
        f_catch_time, fine = qzone_spider.get_fine_json('***REMOVED***', rough_json[i]['tid'], cookie, gtk, qzonetoken)
        if f_catch_time == 0 and fine == -1:
            break
        parse_fine = qzone_spider.fine_json_parse(rough_json, i, fine, f_catch_time)
        db_control_mysql.db_write_fine(parse_fine)
        time.sleep(svar.spiderWaitTime)
