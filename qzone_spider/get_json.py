#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Get JSON of information of Qzone """

__author__ = 'Ding Junyao'

import logging
import requests
from qzone_spider import svar
import time
import re
import json

logger = logging.getLogger(__name__)


def get_rough_json(qq, start, msgnum, replynum, cookies, gtk, qzonetoken):
    fail = 0
    while fail < svar.getRoughJSONFailTime:
        s = requests.session()
        params = {
            'uin': qq,
            'ftype': '0',
            'sort': '0',
            'pos': start,
            'num': msgnum,
            'replynum': replynum,
            'g_tk': gtk,
            'callback': '_preloadCallback',
            'code_version': '1',
            'format': 'jsonp',
            'need_private_comment': '1',
            'qzonetoken': qzonetoken
        }
        catch_time = int(time.time())
        try:
            response = s.request('GET', svar.roughJSON_URL, params=params, headers=svar.requestHeader, cookies=cookies)
        except TimeoutError:
            fail += 1
            if fail == svar.getRoughJSONFailTime:
                break
            logger.warning('''Connection error when getting the rough JSON of messages #%s ~ #%s of %s. 
            Sleep %s seconds before retrying. Remaining retry times: %s'''
                           % (start, start + msgnum - 1, qq, svar.errorWaitTime, svar.getRoughJSONFailTime - fail))
            time.sleep(svar.errorWaitTime)
            continue
        if (response.status_code == 200) & (response.text is not None):
            logger.info('Successfully get the rough JSON of messages #%s ~ #%s of %s' % (start, start + msgnum - 1, qq))
            response_text = response.text
            response_json = json.loads(response_text[17:-2])
            logger.debug('Returned JSON in Python format is %s' % response_json)
            if not re.search('lbs', response_text):
                logger.warning('Get all messages of %s finished, or an error had occurred, please check it' % qq)
                return 0, -1, 0
            return catch_time, start+msgnum-1, response_json['msglist']
        else:
            fail += 1
            if fail == svar.getRoughJSONFailTime:
                break
            logger.warning('''Failed to request when getting the rough JSON of messages #%s ~ #%s of %s. 
            Sleep %s seconds before retrying. Remaining retry times: %s'''
                           % (start, start + msgnum - 1, qq, svar.errorWaitTime, svar.getRoughJSONFailTime - fail))
            logger.debug('HTTP status code is %s' % response.status_code)
            time.sleep(svar.errorWaitTime)
            continue
    logger.error('Failed to get the rough JSON of messages #%s ~ #%s of %s' % (start, start + msgnum - 1, qq))
    return 0, -1, -1


def get_fine_json(qq, tid, cookies, gtk, qzonetoken):
    fail = 0
    while fail < svar.getFineJSONFailTime:
        params_msg = {
            'qzonetoken': qzonetoken,
            'g_tk': gtk,
            'appid': 311,  # 说说是311，分享是202
            'uin': qq,
            'refresh_type': 31,
            'cellid': tid,
            'subid': '',
        }
        s = requests.session()
        catch_time = int(time.time())
        try:
            response_msg = s.request('GET', svar.fineJSON_URL, params=params_msg,
                                     headers=svar.requestHeader, cookies=cookies)
        except TimeoutError:
            fail += 1
            if fail == svar.getFineJSONFailTime:
                break
            logger.warning(
                '''Connection error when getting the JSON of message of %s which tid is %s. 
                Sleep %s seconds before retrying. Remaining retry times: %s'''
                % (qq, tid, svar.errorWaitTime, svar.getFineJSONFailTime - fail))
            time.sleep(svar.errorWaitTime)
            continue
        if (response_msg.status_code == 200) & (response_msg.text is not None):
            response_msg_text = response_msg.text
            response_msg_json = json.loads(response_msg_text)
            if response_msg_json['ret'] >= 0:
                logger.info('Successfully get the JSON of message of %s which tid is %s' % (qq, tid))
                logger.debug('Returned JSON in Python format is %s' % json.dumps(response_msg_json, ensure_ascii=False))
                return catch_time, response_msg_json
            else:
                fail += 1
                if fail == svar.getFineJSONFailTime:
                    break
                logger.warning('''Strange return when getting the JSON of message of %s which tid is %s. 
                Sleep %s seconds before retrying. Remaining retry times: %s'''
                               % (qq, tid, svar.errorWaitTime, svar.getFineJSONFailTime - fail))
                logger.debug('Returned JSON in Python format is %s' % response_msg_json)
                time.sleep(svar.errorWaitTime)
                continue
        else:
            fail += 1
            if fail == svar.getFineJSONFailTime:
                break
            logger.warning(
                '''Failed to request when getting the JSON of message of %s which tid is %s. 
                Sleep %s seconds before retrying. Remaining retry times: %s'''
                % (qq, tid, svar.errorWaitTime, svar.getFineJSONFailTime - fail))
            logger.debug('HTTP status code is %s' % response_msg.status_code)
            time.sleep(svar.errorWaitTime)
            continue
    logger.error('Failed to get the rough JSON of message of %s which tid is %s' % (qq, tid))
    return 0, -1
