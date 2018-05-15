#!/usr/bin/env python3

from qzone_spider import get_login_info
from qzone_spider import get_json
from qzone_spider import json_parse
import logging

logger = logging.getLogger(__name__)


class QzoneSpider(object):

    def __init__(self, spider_qq, spider_qq_password, scan=False, do_emotion_parse=True,
                 login_try_time=2, get_rough_json_try_time=2,
                 get_fine_json_try_time=2, login_wait=3, scan_wait=20, spider_wait=5, error_wait=600, proxy=None,
                 debug=False):
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
            """
            catch_time, msg = get_json.get_fine_json('***REMOVED***', '4f8281307554d9573e2c0200', self.__cookies,
                                                     self.__gtk, self.__qzonetoken, 1, 10)"""
            catch_time, _, msg = get_json.get_rough_json('490424586', 0, 1, 10,
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
            return 0
        else:
            logger.error('Failed to set log info')
            self.__cookies = tmp_cookies
            self.__gtk = tmp_gtk
            self.__qzonetoken = tmp_qzonetoken
            return -1

    def get_rough_json(self, qq, start=0, quantity=20, replynum=10):
        rough_json_list = []
        sub_quantity = quantity % 20
        end_order = start
        while end_order < quantity:
            if end_order + 20 <= quantity:
                spider_quantity = 20
            else:
                spider_quantity = sub_quantity
            r_catch_time, end_order, rough_json = get_json.get_rough_json(qq, start, spider_quantity, replynum,
                                                                          self.__cookies, self.__gtk, self.__qzonetoken,
                                                                          self.get_rough_json_try_time, self.error_wait)
            if r_catch_time == 0 and end_order == -1:
                break
            end_order += 1
        pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(name)s: %(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)
    sp = QzoneSpider(spider_qq='***REMOVED***', spider_qq_password='***REMOVED***', scan=False, do_emotion_parse=True,
                     login_try_time=2, get_rough_json_try_time=2, get_fine_json_try_time=2, login_wait=3, scan_wait=20,
                     spider_wait=5, error_wait=600, proxy=None, debug=False)
    user_cookies = {'skey': '@ThExjTnjq', 'pt2gguin': 'o0***REMOVED***', '_qpsvr_localtk': '0.24119287784595977', 'pgv_pvi': '4202695680', 'uin': 'o0***REMOVED***', 'pgv_si': 's7208889344', 'ptcz': '6c9585ed5f58daad190f5b8fc6c76bef55c918a2b5018eedbd8ec78f1ff0a372', 'pgv_pvid': '5171932800', 'ptisp': 'ctc', 'p_uin': 'o0***REMOVED***', 'pgv_info': 'ssid=s4954116000', 'RK': 'JTiYMszwQU', 'pt4_token': '4gpKXwOXxjN*qj8vUrGSNlajtb18tt78qMCC8dQSc*o_', 'QZ_FE_WEBP_SUPPORT': '1', 'p_skey': 'eiwFR5-chVl50szlF1Tc9BKmXitc2bCIt-FtsSE7Y0M_', 'qqmusic_uin': '', 'fnc': '2', 'Loading': 'Yes', 'qz_screen': '1920x1080', 'qzmusicplayer': 'qzone_player_***REMOVED***_1526358833925', 'qqmusic_key': '', 'qqmusic_fromtag': ''}
    user_gtk = 410675130
    user_qzonetoken = 'bb1187d1d229f95735cdd91ecb216b4fe69eca336458d2c8762bf777ac1f78572c02a302d7244620a3'
    # sp.login()
    sp.set_login_info(user_cookies, user_gtk, user_qzonetoken)
    print(sp.status)
