#!/usr/bin/env python3

"""An example of qzone_spider"""

import qzone_spider
from qzone_spider import db_control_mysql as db_control
from qzone_spider import svar
import logging
import time

QQ = '***REMOVED***'
password = '***REMOVED***'
target = '***REMOVED***'
quantity = 40


logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(name)s: %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

cookie, gtk, qzonetoken = qzone_spider.account_login(QQ, password)
end_order = 0
while end_order < quantity:
    r_catch_time, end_order, rough_json = qzone_spider.get_rough_json(target, end_order, 20, 100, cookie, gtk, qzonetoken)
    if r_catch_time == 0 and end_order == -1:
        break
    end_order += 1
    for i in range(len(rough_json)):
        f_catch_time, fine = qzone_spider.get_fine_json(target, rough_json[i]['tid'], cookie, gtk, qzonetoken)
        if f_catch_time == 0 and fine == -1:
            break
        parse_fine = qzone_spider.fine_json_parse(rough_json, i, fine, f_catch_time)
        db_control.db_write_fine(parse_fine)
        time.sleep(svar.spiderWaitTime)
