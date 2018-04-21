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
            # logger.warning('获取QQ为 %s 的 %s ~ %s 的说说粗略数据时连接异常。休息 %s 秒后重试，剩余重试次数为: %s'
            #                % (qq, start, start + msgnum - 1, svar.errorWaitTime, svar.getRoughJSONFailTime - fail))
            logger.warning('''Connection error when getting the rough JSON of messages #%s ~ #%s of %s. 
            Sleep %s seconds before retrying. Remaining retry times: %s'''
                           % (start, start + msgnum - 1, qq, svar.errorWaitTime, svar.getRoughJSONFailTime - fail))
            time.sleep(svar.errorWaitTime)
            continue
        if (response.status_code == 200) & (response.text is not None):
            # logger.info('获取QQ为 %s 的 %s ~ %s 的说说粗略数据成功' % (qq, start, start + msgnum - 1))
            logger.info('Successfully get the rough JSON of messages #%s ~ #%s of %s' % (start, start + msgnum - 1, qq))
            response_text = response.text
            response_json = json.loads(response_text[17:-2])
            # logger.debug('返回的Python形式的JSON为 %s' % response_json)
            logger.debug('Returned JSON in Python format is %s' % response_json)
            if not re.search('lbs', response_text):
                # logger.warning('获取QQ为 %s 的 全部说说完成，也有可能是操作发生了异常，请核实' % qq)
                logger.warning('Get all messages of %s finished, or an error had occurred, please check it' % qq)
                return 0, -1, 0
            return catch_time, start+msgnum-1, response_json['msglist']
        else:
            fail += 1
            if fail == svar.getRoughJSONFailTime:
                break
            # logger.warning('获取QQ为 %s 的 %s ~ %s 的说说粗略数据时请求失败。休息 %s 秒后重试，剩余重试次数为: %s'
            #                % (qq, start, start + msgnum - 1, svar.errorWaitTime, svar.getRoughJSONFailTime - fail))
            logger.warning('''Failed to request when getting the rough JSON of messages #%s ~ #%s of %s. 
            Sleep %s seconds before retrying. Remaining retry times: %s'''
                           % (start, start + msgnum - 1, qq, svar.errorWaitTime, svar.getRoughJSONFailTime - fail))
            # logger.debug('HTTP状态码为 %s' % response.status_code)
            logger.debug('HTTP status code is %s' % response.status_code)
            time.sleep(svar.errorWaitTime)
            continue
    # logger.error('获取QQ为 %s 的 %s ~ %s 的说说粗略数据失败' % (qq, start, start + msgnum - 1))
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
            logger.warning('获取QQ为 %s 的tid为 %s 的说说JSON时连接异常。休息 %s 秒后重试，剩余重试次数为: %s'
                           % (qq, tid, svar.errorWaitTime, svar.getFineJSONFailTime - fail))
            logger.warning(
                '''Connection error when getting the JSON of message of %s which tid is %s. 
                Sleep %s seconds before retrying. Remaining retry times: %s'''
                % (qq, tid, svar.errorWaitTime, svar.getFineJSONFailTime - fail))
            time.sleep(svar.errorWaitTime)
            continue
        if (response_msg.status_code == 200) & (response_msg.text is not None):
            response_msg_text = response_msg.text  # 读取响应内容
            # print(response_msg_text)
            response_msg_json = json.loads(response_msg_text)
            if response_msg_json['ret'] >= 0:
                # logger.info('获取QQ为 %s 的tid为 %s 的说说JSON成功' % (qq, tid))
                logger.info('Successfully get the JSON of message of %s which tid is %s' % (qq, tid))
                # logger.debug('返回的Python形式的JSON为 %s' % json.dumps(response_msg_json, ensure_ascii=False))
                logger.debug('Returned JSON in Python format is %s' % json.dumps(response_msg_json, ensure_ascii=False))
                return catch_time, response_msg_json
            else:
                fail += 1
                if fail == svar.getFineJSONFailTime:
                    break
                # logger.warning('获取QQ为 %s 的tid为 %s 的说说JSON时返回异常。休息 %s 秒后重试，剩余重试次数为: %s'
                #                % (qq, tid, svar.errorWaitTime, svar.getFineJSONFailTime - fail))
                logger.warning('''Strange return when getting the JSON of message of %s which tid is %s. 
                Sleep %s seconds before retrying. Remaining retry times: %s'''
                               % (qq, tid, svar.errorWaitTime, svar.getFineJSONFailTime - fail))
                # logger.debug('返回的Python形式的JSON为 %s' % response_msg_json)
                logger.debug('Returned JSON in Python format is %s' % response_msg_json)
                time.sleep(svar.errorWaitTime)
                continue
        else:
            fail += 1
            if fail == svar.getFineJSONFailTime:
                break
            # logger.warning('获取QQ为 %s 的tid为 %s 的说说数据时请求失败。休息 %s 秒后重试，剩余重试次数为: %s'
            #                % (qq, tid, svar.errorWaitTime, svar.getFineJSONFailTime - fail))
            logger.warning(
                '''Failed to request when getting the JSON of message of %s which tid is %s. 
                Sleep %s seconds before retrying. Remaining retry times: %s'''
                % (qq, tid, svar.errorWaitTime, svar.getFineJSONFailTime - fail))
            # logger.debug('HTTP状态码为 %s' % response_msg.status_code)
            logger.debug('HTTP status code is %s' % response_msg.status_code)
            time.sleep(svar.errorWaitTime)
            continue
    # logger.error('获取QQ为 %s 的tid为 %s 的说说数据失败' % (qq, tid))
    logger.error('Failed to get the rough JSON of message of %s which tid is %s' % (qq, tid))
    return 0, -1
