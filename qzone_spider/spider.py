#!/usr/bin/env python3

"""An example of qzone_spider"""

import qzone_spider
from qzone_spider import db_control_sqlite as db_control
import logging
import time
import argparse
import getpass
import sys


def main():
    parser = argparse.ArgumentParser(description='An example of qzone_spider')
    parser.add_argument('user', help="QQ number as the spider", type=str)
    parser.add_argument('target', help="QQ number as the target", type=str)
    parser.add_argument('-p', '--password', help="password of the spider QQ, if you don't add it, you can input it later",
                        type=str)
    parser.add_argument('-q', '--quantity', help="the quantity of the spider, must be a multiple of 5 (default: 5)",
                        type=int, default=5)
    parser.add_argument('-i', '--init', help="init the database of the spider with it, add it at first run",
                        action="store_true")
    parser.add_argument('-d', '--debug', help="open GUI environment of browser with it", action="store_true")
    parser.add_argument('-l', '--loglevel', help="set the log level (debug, info, warning, error)", type=str, default='info')
    args = parser.parse_args()
    if args.init:
        db_control.db_init()
    QQ = args.user
    targetQQ = args.target
    quantity = args.quantity
    if args.loglevel.lower == 'info':
        log_level = logging.INFO
    elif args.loglevel.lower == 'debug':
        log_level = logging.DEBUG
    elif args.loglevel.lower == 'warning':
        log_level = logging.WARNING
    elif args.loglevel.lower == 'error':
        log_level = logging.ERROR
    else:
        log_level = logging.INFO
    if args.password:
        password = args.password
    else:
        password = getpass.getpass("Password: ")
    logging.basicConfig(level=log_level, format='[%(asctime)s] %(name)s: %(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)
    cookies, gtk, qzonetoken = qzone_spider.account_login(QQ, password, debug=args.debug)
    end_order = 0
    while end_order < quantity:
        r_catch_time, end_order, rough_json = qzone_spider.get_rough_json(
            targetQQ, end_order, 1, 10, cookies, gtk, qzonetoken)
        if r_catch_time == 0 and end_order == -1:
            break
        end_order += 1
        for i in range(len(rough_json)):
            f_catch_time, fine = qzone_spider.get_fine_json(targetQQ, rough_json[i]['tid'], cookies, gtk, qzonetoken)
            if f_catch_time == 0 and fine == -1:
                break
            parse_fine = qzone_spider.fine_json_parse(rough_json, i, fine, f_catch_time)
            db_control.db_write_fine(parse_fine)
            if i != len(rough_json) - 1 or end_order < quantity:
                time.sleep(qzone_spider.svar.spiderWaitTime)


if __name__ == "__main__":
    sys.exit(main())
