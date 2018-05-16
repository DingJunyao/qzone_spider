#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Get JSON of information of Qzone """

__author__ = 'Ding Junyao'

import logging
import requests
import time
import re
import json

request_header = {
    'Host': 'h5.qzone.qq.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0',
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://qzone.qq.com/',
    'Connection': 'keep-alive'
}

logger = logging.getLogger(__name__)


def get_rough_json(qq, start, msgnum, replynum, cookies, gtk, qzonetoken, get_rough_json_try_time=2,
                   error_wait=600):
    if msgnum > 20:
        msgnum = 20
        logger.warning('msgnum should be less than 20. Change it to 20')
    if start < 0:
        start = 0
        logger.warning('start should not be less than 0. Change it to 0')
    rough_json_url = 'https://h5.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6'
    fail = 0
    while fail < get_rough_json_try_time:
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
            response = s.request('GET', rough_json_url, params=params, headers=request_header, cookies=cookies)
        except Exception:
            fail += 1
            if fail == get_rough_json_try_time:
                break
            logger.warning('''Connection error when getting the rough JSON of messages #%s ~ #%s of %s.
Sleep %s seconds before retrying. Remaining retry times: %s'''
                           % (start, start + msgnum - 1, qq, error_wait, get_rough_json_try_time - fail))
            time.sleep(error_wait)
            continue
        if (response.status_code == 200) & (response.text is not None):
            response_text = response.text
            response_json = json.loads(response_text[17:-2])
            logger.debug('Returned JSON in Python format is %s' % response_json)
            if response_json['message'] == '请先登录空间':
                logger.error('Log info invalid or expired')
                return 0, -1, -2
            if response_json['message'] == '对不起,主人设置了保密,您没有权限查看':
                logger.error('''Can not access to Qzone of %s. 
If the owner does not set authority, maybe the Qzone is blocked by official''' % qq)
                return 0, -1, -3
            if response_json['msglist'] == '':
                logger.warning('No message in the range #%s ~ #%s of %s, maybe finished'
                               % (start, start + msgnum - 1, qq))
                return 0, -1, 0
            real_msg_num = len(response_json['msglist'])
            logger.info('Successfully get the rough JSON of messages #%s ~ #%s of %s'
                        % (start, start + real_msg_num - 1, qq))
            if real_msg_num != msgnum:
                logger.info('Get all messages of %s finished' % qq)
                return catch_time, -1, response_json['msglist']
            return catch_time, start + real_msg_num - 1, response_json['msglist']
        else:
            fail += 1
            if fail == get_rough_json_try_time:
                break
            logger.warning('''Failed to request when getting the rough JSON of messages #%s ~ #%s of %s.
Sleep %s seconds before retrying. Remaining retry times: %s'''
                           % (start, start + msgnum - 1, qq, error_wait, get_rough_json_try_time - fail))
            logger.debug('HTTP status code is %s' % response.status_code)
            time.sleep(error_wait)
            continue
    logger.error('Failed to get the rough JSON of messages #%s ~ #%s of %s' % (start, start + msgnum - 1, qq))
    return 0, -1, -1


def get_fine_json(qq, tid, cookies, gtk, qzonetoken, get_fine_json_try_time=2, error_wait=600):
    fine_json_url = 'https://h5.qzone.qq.com/webapp/json/mqzone_detail/shuoshuo'
    fail = 0
    while fail < get_fine_json_try_time:
        params_msg = {
            'qzonetoken': qzonetoken,
            'g_tk': gtk,
            'appid': 311,
            'uin': qq,
            'refresh_type': 31,
            'cellid': tid,
            'subid': '',
        }
        s = requests.session()
        catch_time = int(time.time())
        try:
            response_msg = s.request('GET', fine_json_url, params=params_msg,
                                     headers=request_header, cookies=cookies)
        except Exception:
            fail += 1
            if fail == get_fine_json_try_time:
                break
            logger.warning(
                '''Connection error when getting the JSON of message of %s which tid is %s.
                Sleep %s seconds before retrying. Remaining retry times: %s'''
                % (qq, tid, error_wait, get_fine_json_try_time - fail))
            time.sleep(error_wait)
            continue
        if (response_msg.status_code == 200) & (response_msg.text is not None):
            response_msg_text = response_msg.text
            response_msg_json = json.loads(response_msg_text)
            if response_msg_json['ret'] >= 0:
                logger.info('Successfully get the JSON of message of %s which tid is %s' % (qq, tid))
                logger.debug('Returned JSON in Python format is %s' % json.dumps(response_msg_json, ensure_ascii=False))
                return catch_time, response_msg_json
            else:
                if response_msg_json['message'] == '没有登录态':
                    logger.error('Log info invalid or expired')
                    return 0, -2
                if response_msg_json['message'] == '没有权限访问':
                    logger.error('''Can not access to Qzone of %s. 
If the owner does not set authority, maybe the Qzone is blocked by official''' % qq)
                    return 0, -3
                if response_msg_json['message'] == '说说通用失败':
                    logger.error('tid not exist')
                    return 0, -4
                fail += 1
                if fail == get_fine_json_try_time:
                    break
                logger.warning('''Strange return when getting the JSON of message of %s which tid is %s.
Sleep %s seconds before retrying. Remaining retry times: %s'''
                               % (qq, tid, error_wait, get_fine_json_try_time - fail))
                logger.debug('Returned JSON in Python format is %s' % response_msg_json)
                time.sleep(error_wait)
                continue
        else:
            fail += 1
            if fail == get_fine_json_try_time:
                break
            logger.warning(
                '''Failed to request when getting the JSON of message of %s which tid is %s.
Sleep %s seconds before retrying. Remaining retry times: %s'''
                % (qq, tid, error_wait, get_fine_json_try_time - fail))
            logger.debug('HTTP status code is %s' % response_msg.status_code)
            time.sleep(error_wait)
            continue
    logger.error('Failed to get the rough JSON of message of %s which tid is %s' % (qq, tid))
    return 0, -1
