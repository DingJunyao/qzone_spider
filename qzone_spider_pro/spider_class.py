#!/usr/bin/env python3

from qzone_spider_pro import get_login_info
from qzone_spider_pro import get_json
from qzone_spider_pro import json_parse
import logging


class QzoneSpider(object):

    def __init__(self, spider_qq, spider_qq_password, scan=False, do_emotion_parse=True,
                 login_try_time=2, get_rough_json_try_time=2,
                 get_fine_json_try_time=2, login_wait=3, scan_wait=20, spider_wait=5, error_wait=600, proxy=None,
                 debug=False):
        logger = logging.getLogger(__name__)
        self.status = 'init'
        self.queue = []
        self.spider_qq = spider_qq
        self.spider_qq_password = spider_qq_password
        self.scan = scan
        self.do_emotion_parse = do_emotion_parse
        self.login_try_time = login_try_time
        self.get_rough_json_try_time = get_rough_json_try_time
        self.get_fine_json_try_time = get_fine_json_try_time
        self.login_wait = login_wait
        self.scan_wait = scan_wait
        self.spider_wait = spider_wait
        self.error_wait = error_wait
        self.proxy = proxy
        self.debug = debug
        self.__cookies = None
        self.__gtk = None
        self.__qzonetoken = None

    def check_login_info(self):
        if self.__cookies is None or self.__gtk is None or self.__qzonetoken is None:
            logger.warning('No log info')
            return -1
        else:

            """catch_time, msg = get_json.get_fine_json('490424586', '4f8281307554d9573e2c0200', self.__cookies,
                                         self.__gtk, self.__qzonetoken, 1, 10)"""
            catch_time, _, msg = get_json.get_rough_json(self.spider_qq, 0, 1, 10,
                                 self.__cookies, self.__gtk, self.__qzonetoken, 1, 0)
            if msg == -1 or msg == -2:
                logger.error('Can not get data with current log info')
                return 1
            else:
                return 0

    def login(self):
        self.status = 'login'
        if self.scan is True:
            self.__cookies, self.__gtk, self.__qzonetoken = get_login_info.scan_login(self.login_try_time,
                                                                                      self.scan_wait,  self.error_wait)
        else:
            self.__cookies, self.__gtk, self.__qzonetoken = get_login_info.account_login(self.spider_qq,
                                                                                         self.spider_qq_password,
                                                                                         self.debug,
                                                                                         self.login_try_time,
                                                                                         self.login_wait,
                                                                                         self.error_wait)
        if self.check_login_info() == 0:
            self.status = 'idle'
            return 0
        else:
            logger.error('Failed to get log info')
            return -1

    def set_login_info(self, cookies, gtk, qzonetoken):
        tmp_cookies = self.__cookies
        tmp_gtk = self.__gtk
        tmp_qzonetoken = self.__qzonetoken
        self.__cookies = cookies
        self.__gtk = gtk
        self.__qzonetoken = qzonetoken
        if self.check_login_info() == 0:
            self.status = 'idle'
            logger.info('Successfully set log info')
            return 0
        else:
            logger.error('Failed to set log info')
            self.__cookies = tmp_cookies
            self.__gtk = tmp_gtk
            self.__qzonetoken = tmp_qzonetoken
            return -1

    def get_rough_json(self, qq, start=0, quantity=20, replynum=10):
        self.status = 'working'
        rough_json_list = []
        sub_quantity = quantity % 20
        end_order = start
        while end_order < quantity:
            if end_order + 20 <= quantity:
                spider_quantity = 20
            else:
                spider_quantity = sub_quantity
            r_catch_time, end_order, rough_json = get_json.get_rough_json(qq, end_order, spider_quantity, replynum,
                                                                          self.__cookies, self.__gtk, self.__qzonetoken,
                                                                          self.get_rough_json_try_time, self.error_wait)
            rough_json_list.append({'catch_time': r_catch_time, 'msglist': rough_json})
            if r_catch_time == 0 and end_order == -1:
                break
            end_order += 1
        self.status = 'idle'
        return rough_json_list

    def rough_json_parse(self, rough_json_list):
        self.status = 'working'
        rough_data = []
        for rough_json_set in rough_json_list:
            for i in range(len(rough_json_set['msglist'])):
                rough_data_item = json_parse.rough_json_parse(rough_json_set['msglist'], i,
                                                              rough_json_set['catch_time'], self.do_emotion_parse)
                rough_data.append(rough_data_item)
        self.status = 'idle'
        return rough_data

    def rough_spider(self, qq, start=0, quantity=20, replynum=10):
        self.status = 'working'
        rough_json_list = self.get_rough_json(qq, start, quantity, replynum)
        rough_data = self.rough_json_parse(rough_json_list)
        return rough_data

    def get_fine_json_from_rough_json_list(self, rough_json_list):
        self.status = 'working'
        fine_json_list = []
        for rough_json_set in rough_json_list:
            for i in range(len(rough_json_set['msglist'])):
                f_catch_time, fine_json = get_json.get_fine_json(rough_json_set['msglist'][i]['uin'],
                                                                 rough_json_set['msglist'][i]['tid'],
                                                                 self.__cookies, self.__gtk, self.__qzonetoken,
                                                                 self.get_fine_json_try_time, self.error_wait)
                if f_catch_time == 0:
                    if fine_json == -2:
                        self.login()
                        i -= 1
                        continue
                    elif fine_json == -6:
                        self.status = 'invalid'
                        # TODO: 添加替换账号的操作
                        return fine_json_list
                    else:
                        f_catch_time = None
                        fine_json = None
                fine_json_list.append({'rough_catch_time': rough_json_set['catch_time'],
                                       'rough_json': rough_json_set['msglist'][i],
                                       'fine_catch_time': f_catch_time,
                                       'fine_json': fine_json})
        self.status = 'idle'
        return fine_json_list

    def fine_json_parse(self, fine_json_list):
        self.status = 'working'
        fine_data = []
        for fine_json_set in fine_json_list:
            if fine_json_set['fine_json'] is None:
                one_fine_data = json_parse.rough_json_parse(fine_json_set['rough_json'], 0,
                                                            fine_json_set['rough_catch_time'], self.do_emotion_parse,
                                                            single_rough_json=True)
            else:
                one_fine_data = json_parse.fine_json_parse(fine_json_set['rough_json'], 0, fine_json_set['fine_json'],
                                                           fine_json_set['fine_catch_time'], self.do_emotion_parse,
                                                           single_rough_json=True)
            fine_data.append(one_fine_data)
        self.status = 'idle'
        return fine_data

    def fine_spider(self, qq, start=0, quantity=20, replynum=10):
        self.status = 'working'
        rough_json_list = self.get_rough_json(qq, start, quantity, replynum)
        fine_json_list = self.get_fine_json_from_rough_json_list(rough_json_list)
        fine_data = self.fine_json_parse(fine_json_list)
        self.status = 'idle'
        return fine_data


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(name)s: %(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)
    sp = QzoneSpider(spider_qq='***REMOVED***', spider_qq_password='***REMOVED***', scan=False, do_emotion_parse=True,
                     login_try_time=2, get_rough_json_try_time=2, get_fine_json_try_time=2, login_wait=3, scan_wait=20,
                     spider_wait=5, error_wait=600, proxy=None, debug=False)
    user_cookies = {'ptisp': 'ctc', 'x-stgw-ssl-info': '951b344f2c1efe282d8dbf5dffff9c07_0.487_1526540831.248_1_h2_N_Y_TLSv1.2_ECDHE-RSA-AES128-GCM-SHA256_80500_0', '_qz_referrer': 'qzone.qq.com', 'pgv_pvi': '8946716672', 'uin': 'o0***REMOVED***', 'pgv_si': 's8135552000', 'skey': '@Vtjg7BS4a', 'pt2gguin': 'o0***REMOVED***', 'RK': 'CTiQdszhS0', 'ptcz': '0730fdf35601e86da19212118a349611045f22a7405cabe8f45e3d2ac60ac0d8', 'p_uin': 'o0***REMOVED***', 'pt4_token': 'qGDSO6bA1ARxYKpSeXApjHXPygRyFCtjhvEgiT9wH6E_', 'p_skey': 'f*ll9Lnix92kdrC5tI8HDCx*6F-wmxrOPHf96sUuUcM_'}
    user_gtk = 1990862463
    user_qzonetoken = '00d5b8760c5db2f23aca0276d273a167abec2f01367b38b1604dee40faf50aeb564b40b4a98ade452b2ed697f87a50f8'
    if sp.set_login_info(user_cookies, user_gtk, user_qzonetoken) != 0:
        sp.login()
    print(sp.status)
    print(sp.fine_spider('***REMOVED***', 0, 63))
