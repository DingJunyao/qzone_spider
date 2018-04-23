#!/usr/bin/env python3

"""An example of qzone_spider"""

import qzone_spider
from qzone_spider import db_control_mysql as db_control
from qzone_spider import svar
import logging
import time
import argparse

parser = argparse.ArgumentParser(description='manual to this script')
parser.add_argument('-u', type=str, default=None)
parser.add_argument('-p', type=str, default=None)
parser.add_argument('-t', type=str, default=None)
parser.add_argument('-q', type=int, default=20)
args = parser.parse_args()

QQ = args.u
password = args.p
targetQQ = args.t
quantity = args.q

if QQ is None or targetQQ is None:
    print(
        '''Usage: ./spider_example.py -u your_QQ_number -q quantity
    quantity must be a multiple of 5''')
    exit()

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(name)s: %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

cookies, gtk, qzonetoken = qzone_spider.account_login(QQ, password)
end_order = 0
while end_order < quantity:
    r_catch_time, end_order, rough_json = qzone_spider.get_rough_json(targetQQ, end_order, 5, 100,
                                                                      cookies, gtk, qzonetoken)
    if r_catch_time == 0 and end_order == -1:
        break
    end_order += 1
    for i in range(len(rough_json)):
        f_catch_time, fine = qzone_spider.get_fine_json(targetQQ, rough_json[i]['tid'], cookies, gtk, qzonetoken)
        if f_catch_time == 0 and fine == -1:
            break
        parse_fine = qzone_spider.fine_json_parse(rough_json, i, fine, f_catch_time)
        db_control.db_write_fine(parse_fine)
        time.sleep(svar.spiderWaitTime)
