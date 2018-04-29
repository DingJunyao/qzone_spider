#!/usr/bin/env python3

"""An example of qzone_spider"""

import qzone_spider
import logging
import time
import argparse
import getpass
import sys
import configparser
import os


def main():
    config = configparser.ConfigParser()
    parser = argparse.ArgumentParser(description='An example of qzone_spider')
    parser.add_argument('target', help="QQ number as the target", type=str)
    parser.add_argument('-u', '--user',
                        help="QQ number as the spider; if you login via QR Code scan, you needn't input it",
                        type=str)
    parser.add_argument('-p', '--password',
                        help="password of the spider QQ, \
                        if you don't add it and you choose login with QQ and password, you can input it later",
                        type=str)
    parser.add_argument('-s', '--start', help="the start position of the spider (default: 0)",
                        type=int, default=0)
    parser.add_argument('-q', '--quantity', help="the quantity of the spider (default: 5)",
                        type=int, default=5)
    parser.add_argument('-i', '--init', help="init the database of the spider with it, add it at first run",
                        action="store_true")
    parser.add_argument('-d', '--debug', help="open GUI environment of browser with it", action="store_true")
    parser.add_argument('-l', '--loglevel', help="set the log level (debug, info, warning, error) (default: info)",
                        type=str, default='info')
    parser.add_argument('-c', '--config',
                        help="load a config file, the application will create it if it doesn't exist \
                             (default: qzone-spider.conf)", type=str, default='qzone-spider.conf')
    args = parser.parse_args()
    if not os.path.exists(args.config):
        print('=' * 40 + "\nThe config file \"%s\" doesn't exist, it will be create soon,\
and you need to configure it." % args.config)
        db_url, db_port, db_database, db_username, db_password = '', '', '', '', ''
        print('=' * 40 +
              '''\nPlease select database type: 
\t[1] MySQL or MariaDB
\t[2] PostgreSQL
\t[3] SQLite
Default: [3] SQLite''')
        while True:
            db_type_num = input('Database type: ')
            if db_type_num == '1':
                db_type = 'MySQL'
                db_port = 3306
                break
            elif db_type_num == '2':
                db_type = 'PostgreSQL'
                db_port = 5432
                break
            elif db_type_num == '3' or db_type_num == '':
                db_type = 'SQLite'
                break
            else:
                print('Your choice must be 1, 2 or 3!')
        print('-'*40)
        if db_type == 'SQLite':
            db_url = input('Please input database file path (Default: qzone.db)\nDatabase File Path: ')
            if db_url == '':
                db_url = 'qzone.db'
        else:
            db_url = input("Please input database URL.\nURL doesn't contain protocol like 'http://'\nDatabase URL: ")
        if db_type == 'MySQL' or db_type == 'PostgreSQL':
            print('-' * 40 + '\nPlease input database port.\nDefault Port: %s' % db_port)
            while True:
                db_port_str = input('Database Port: ')
                if db_port_str != '':
                    if db_port_str.isdigit() and 0 <= int(db_port_str) <= 65535:
                        db_port = int(db_port_str)
                        break
                    else:
                        print('Database port must be integer between 0 and 65535! ')
                else:
                    break
            db_database = input('-'*40 + '\nPlease input database name: ')
            db_username = input('-'*40 + '\nPlease input database user name: ')
            db_password = getpass.getpass('-' * 40 + '\nPlease input user "%s"\'s password: ' % db_username)
        print('=' * 40)
        print('''Which login mode do you want, with QQ and password or via QR Code?
Login via QR Code ensures your account security better, but it requires GUI environment all the time. 
\t[0] Login with QQ and password
\t[1] Login via QR Code scanning
Default: [0] Login with QQ and password''')
        while True:
            scan_mode_str = input('Choose: ')
            if scan_mode_str != '':
                if scan_mode_str.isdigit() and (int(scan_mode_str) == 0 or int(scan_mode_str) == 1):
                    scan_mode = int(scan_mode_str)
                    break
                else:
                    print('Your choice must be 1 or 0! ')
            else:
                scan_mode = 0
                break
        print('-' * 40)
        print('''Which spider mode do you want, rough or fine?
Fine mode can get more information than rough mode, but fine mode is slower, and you can't use it frequently in case \
of restriction of QQ. 
\t[0] Rough
\t[1] Fine
Default: [1] Fine''')
        while True:
            fine_mode_str = input('Choose: ')
            if fine_mode_str != '':
                if fine_mode_str.isdigit() and (int(fine_mode_str) == 0 or int(fine_mode_str) == 1):
                    fine_mode = int(fine_mode_str)
                    break
                else:
                    print('Your choice must be 1 or 0! ')
            else:
                fine_mode = 1
                break
        print('-' * 40)
        print('''Do you want to parse the emotion strings to readable emotion strings or emoji?
For example: [em]e100[/em] -> [/微笑]; [em]e401181[/em] -> ☺
They can be stored and read properly, but not all database viewers support showing emoji.
\t[1] Yes
\t[0] No
Default: [1] Yes''')
        while True:
            do_emotion_parse_str = input('Choose: ')
            if do_emotion_parse_str != '':
                if do_emotion_parse_str.isdigit() and (
                        int(do_emotion_parse_str) == 0 or int(do_emotion_parse_str) == 1):
                    do_emotion_parse = int(do_emotion_parse_str)
                    break
                else:
                    print('Your choice must be 1 or 0! ')
            else:
                do_emotion_parse = 1
                break
        print('='*40)
        while True:
            login_try_time_str = input('Please input max times trying to get login information (Default: 2): ')
            if login_try_time_str != '':
                if login_try_time_str.isdigit() and int(login_try_time_str) >= 1:
                    login_try_time = int(login_try_time_str)
                    break
                else:
                    print('Times must be integer not smaller than 1!')
            else:
                login_try_time = 2
                break
        print('-' * 40)
        while True:
            get_rough_json_try_time_str = input('Please input max times trying to get rough JSON (Default: 2): ')
            if get_rough_json_try_time_str != '':
                if get_rough_json_try_time_str.isdigit() and int(get_rough_json_try_time_str) >= 1:
                    get_rough_json_try_time = int(get_rough_json_try_time_str)
                    break
                else:
                    print('Times must be integer not smaller than 1!')
            else:
                get_rough_json_try_time = 2
                break
        print('-' * 40)
        while True:
            get_fine_json_try_time_str = input('Please input max times trying to get fine JSON (Default: 2): ')
            if get_fine_json_try_time_str != '':
                if get_fine_json_try_time_str.isdigit() and int(get_fine_json_try_time_str) >= 1:
                    get_fine_json_try_time = int(get_fine_json_try_time_str)
                    break
                else:
                    print('Times must be integer not smaller than 1!')
            else:
                get_fine_json_try_time = 2
                break
        print('=' * 40)
        while True:
            login_wait_str = input('Please input wait seconds when load login site (Default: 3): ')
            if login_wait_str != '':
                if login_wait_str.isdigit() and int(login_wait_str) >= 1:
                    login_wait = int(login_wait_str)
                    break
                else:
                    print('Seconds must be integer not smaller than 1!')
            else:
                login_wait = 3
                break
        print('-' * 40)
        while True:
            scan_wait_str = input('Please input seconds waiting for scan QR Code (Default: 20): ')
            if scan_wait_str != '':
                if scan_wait_str.isdigit() and int(scan_wait_str) >= 1:
                    scan_wait = int(scan_wait_str)
                    break
                else:
                    print('Seconds must be integer not smaller than 1!')
            else:
                scan_wait = 20
                break
        print('-' * 40)
        while True:
            spider_wait_str = input('Please input wait seconds between getting information (Default: 5): ')
            if spider_wait_str != '':
                if spider_wait_str.isdigit() and int(spider_wait_str) >= 1:
                    spider_wait = int(spider_wait_str)
                    break
                else:
                    print('Seconds must be integer not smaller than 1!')
            else:
                spider_wait = 5
                break
        print('-' * 40)
        while True:
            error_wait_str = input('Please input wait seconds when error happens (Default: 600): ')
            if error_wait_str != '':
                if error_wait_str.isdigit() and int(error_wait_str) >= 1:
                    error_wait = int(error_wait_str)
                    break
                else:
                    print('Seconds must be integer not smaller than 1!')
            else:
                error_wait = 600
                break
        print('=' * 40)
        config.read(args.config)
        config.add_section('database')
        config.set('database', 'type', db_type)
        config.set('database', 'url', db_url)
        config.set('database', 'port', str(db_port))
        config.set('database', 'database', db_database)
        config.set('database', 'username', db_username)
        config.set('database', 'password', db_password)
        config.add_section('mode')
        config.set('mode', 'scan', str(scan_mode))
        config.set('mode', 'fine', str(fine_mode))
        config.set('mode', 'do_emotion_parse', str(do_emotion_parse))
        config.add_section('try')
        config.set('try', 'login_try_time', str(login_try_time))
        config.set('try', 'get_rough_json_try_time', str(get_rough_json_try_time))
        config.set('try', 'get_fine_json_try_time', str(get_fine_json_try_time))
        config.add_section('wait')
        config.set('wait', 'login_wait', str(login_wait))
        config.set('wait', 'scan_wait', str(scan_wait))
        config.set('wait', 'spider_wait', str(spider_wait))
        config.set('wait', 'error_wait', str(error_wait))
        config.write(open(args.config, 'w'))
        print('Setup finished, and you need to remember the absolute path to the config file: \n\t%s'
              % os.path.abspath(args.config))
        print('Note that the file is written in plain text, so keep it secret if necessary in case of password stolen.')
        if db_type == 'SQLite':
            print('If you define a relative path to SQLite database file, \
remember it is based on the directory where config file is in. ')
            print('Absolute path to the database file:\n\t%s' % os.path.abspath(db_url))
        print('=' * 40)
    config.read(args.config)
    db_type = config.get('database', 'type')
    db_url = config.get('database', 'url')
    if db_type == 'MySQL':
        from qzone_spider import db_control_mysql as db_control
        db_port = int(config.get('database', 'port'))
        db_database = config.get('database', 'database')
        db_username = config.get('database', 'username')
        db_password = config.get('database', 'password')
    elif db_type == 'PostgreSQL':
        from qzone_spider import db_control_postgresql as db_control
        db_port = int(config.get('database', 'port'))
        db_database = config.get('database', 'database')
        db_username = config.get('database', 'username')
        db_password = config.get('database', 'password')
    elif db_type == 'SQLite':
        from qzone_spider import db_control_sqlite as db_control
        db_port, db_database, db_username, db_password = None, None, None, None
    else:
        print('Config file error!')
        return -1
    scan_mode = config.getboolean('mode', 'scan')
    fine_mode = config.getboolean('mode', 'fine')
    do_emotion_parse = config.getboolean('mode', 'do_emotion_parse')
    login_try_time = int(config.get('try', 'login_try_time'))
    get_rough_json_try_time = int(config.get('try', 'get_rough_json_try_time'))
    get_fine_json_try_time = int(config.get('try', 'get_fine_json_try_time'))
    login_wait = int(config.get('wait', 'login_wait'))
    scan_wait = int(config.get('wait', 'scan_wait'))
    spider_wait = int(config.get('wait', 'spider_wait'))
    error_wait = int(config.get('wait', 'error_wait'))
    if args.loglevel.lower() == 'info':
        log_level = logging.INFO
    elif args.loglevel.lower() == 'debug':
        log_level = logging.DEBUG
    elif args.loglevel.lower() == 'warning':
        log_level = logging.WARNING
    elif args.loglevel.lower() == 'error':
        log_level = logging.ERROR
    else:
        log_level = logging.INFO
    logging.basicConfig(level=log_level, format='[%(asctime)s] %(name)s: %(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)
    if args.init:
        if db_type == 'SQLite':
            db_control.db_init(db_url)
        else:
            db_control.db_init(db_url, db_database, db_username, db_password, db_port)
    if args.start < 0:
        print('-s or --start must be not smaller than 0!')
        return -1
    if args.quantity <= 0:
        print('-q or --quantity must be bigger than 0!')
        return -1
    if scan_mode:
        cookies, gtk, qzonetoken = qzone_spider.scan_login(login_try_time=login_try_time, scan_wait=scan_wait,
                                                           error_wait=error_wait)
    else:
        if not args.user:
                print('QQ number as the spider required!')
                return -1
        else:
            if args.password:
                password = args.password
            else:
                password = getpass.getpass("Password: ")
            cookies, gtk, qzonetoken = qzone_spider.account_login(args.user, password, debug=args.debug,
                                                                  login_try_time=login_try_time, login_wait=login_wait,
                                                                  error_wait=error_wait)
    sub_quantity = args.quantity % 20
    end_order = args.start
    while end_order < args.quantity:
        if end_order + 20 <= args.quantity:
            spider_quantity = 20
        else:
            spider_quantity = sub_quantity
        r_catch_time, end_order, rough_json = qzone_spider.get_rough_json(
            args.target, end_order, spider_quantity, 10, cookies, gtk, qzonetoken,
            get_rough_json_try_time=get_rough_json_try_time, error_wait=error_wait)
        if r_catch_time == 0 and end_order == -1:
            break
        end_order += 1
        for i in range(len(rough_json)):
            if fine_mode:
                f_catch_time, fine = qzone_spider.get_fine_json(args.target, rough_json[i]['tid'],
                                                                cookies, gtk, qzonetoken,
                                                                get_fine_json_try_time=get_fine_json_try_time,
                                                                error_wait=error_wait)
                if f_catch_time == 0 and fine == -1:
                    break
                parse_fine = qzone_spider.fine_json_parse(rough_json, i, fine, f_catch_time,
                                                          do_emotion_parse=do_emotion_parse)
                if db_type == 'SQLite':
                    db_control.db_write_fine(parse_fine, db_url)
                else:
                    db_control.db_write_fine(parse_fine, db_url, db_database, db_username, db_password,
                                             db_port=db_port)
            else:
                parse_rough = qzone_spider.rough_json_parse(rough_json, i, r_catch_time,
                                                            do_emotion_parse=do_emotion_parse)
                if db_type == 'SQLite':
                    db_control.db_write_rough(parse_rough, db_url)
                else:
                    db_control.db_write_rough(parse_rough, db_url, db_database, db_username, db_password,
                                              db_port=db_port)
            if i != len(rough_json) - 1 or end_order < args.quantity:
                time.sleep(spider_wait)
    logger.info('Spider task finishes')
    return 0


if __name__ == "__main__":
    sys.exit(main())
