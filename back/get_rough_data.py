#!/usr/bin/env python3
import logging
import requests
from qzone_spider import svar
import time
import re
import json

"""
get_rough_data.py
Author: Ding Junyao

Function:
Get the rough data of the qzone.
It run with the number

get_rough_json(qq, start, msgnum, replynum, cookie, gtk, qzonetoken)

In:
登录信息
QQ号
起始位置号
信息数量

Out:
捕获时间（时间戳）
结束位置号
一个包含msg的tid的数组

注：本函数暂不支持读取链接分享类说说、相册类说说，需要使用新的数据源并作解析。

"""

logger = logging.getLogger(__name__)

'''
def get_target_qq(uid):
    conn = pymysql.connect(svar.dbURL, svar.dbUsername, svar.dbPassword, svar.dbDatabase, charset="utf8", use_unicode=True)
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT target_qq, mode FROM target WHERE uid = ' + uid + ';')
        results = cursor.fetchall()
        target_qq = []
        for row in results:
            target_qq.append([results[row][0],results[row][1]])
        return target_qq
    except Exception:
        print('Error when getting target_qq')
        return ''
'''


def get_rough_json(qq, start, msgnum, replynum, cookie, gtk, qzonetoken):
    fail = 0
    while fail < svar.getRoughDataFailTime:
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
        response = s.request('GET', svar.roughJSON_URL, params=params, headers=svar.requestHeader, cookies=cookie)
        if (response.status_code == 200) & (response.text is not None):
            logger.info('获取QQ为 %s 的 %s ~ %s 的说说粗略数据成功' % (qq, start, start + msgnum - 1))
            response_text = response.text
            if (response.status_code == 200) & (response.text is not None):
                response_json = json.loads(response_text[17:-2])
                logger.debug('返回的Python形式的JSON为 %s' % response_json)
                if not re.search('lbs', response_text):
                    logger.warning('获取QQ为 %s 的 全部说说完成，也有可能是操作发生了异常，请核实' % qq)
                    return 0, -1, 0
                return catch_time, start+msgnum-1, response_json['msglist']
            else:
                return 0, -1, -2
        else:
            fail += 1
            if fail == svar.getFineDataFailTime:
                break
            logger.warning('获取QQ为 %s 的 %s ~ %s 的说说粗略数据时请求失败，休息 %s 秒后继续，剩余重试次数为: %s' % (qq, start, start + msgnum - 1, svar.errorWaitTime, svar.getRoughDataFailTime - fail))
            logger.debug('HTTP状态码为 %s' % response.status_code)
            time.sleep(svar.errorWaitTime)
    logger.error('获取QQ为 %s 的 %s ~ %s 的说说粗略数据失败' % (qq, start, start + msgnum - 1))
    return 0, -1, -1


def rough_json_parse(rough_json_set, ordernum, catch_time=0):
    rough_json = rough_json_set[ordernum]
    parse = {}
    parse['catch_time'] = catch_time
    parse['tid'] = rough_json['tid']
    parse['qq'] = rough_json['uin']
    parse['post_time'] = rough_json['created_time']
    if 'rt_tid' in rough_json:
        parse['rt_tid'] = rough_json['rt_tid']
    else:
        parse['rt_tid'] = None
    if 'content' in rough_json and rough_json['content'] != '':
        parse['content'] = rough_json['content']
    else:
        parse['content'] = None
    if 'pictotal' in rough_json and 'rt_tid' not in rough_json:
        parse['picnum'] = rough_json['pictotal']
    else:
        parse['picnum'] = 0
    if 'videototal' in rough_json and 'rt_tid' not in rough_json:
        parse['videonum'] = rough_json['videototal']
    else:
        parse['videonum'] = 0
    if 'voice' in rough_json:
        parse['voice'] = {}
        parse['voice']['url'] = rough_json['voice'][0]['url']
        parse['voice']['time'] = rough_json['voice'][0]['time']
    else:
        parse['voice'] = None
    parse['sharelink'] = None  # TODO: 使用新的粗数据源即可使用。
    if 'source_name' in rough_json:
        parse['device'] = rough_json['source_name']
    else:
        parse['device'] = None
    if rough_json['lbs']['idname'] == '':
        if 'story_info' in rough_json:
            parse['location_user'] = rough_json['story_info']['lbs']['idname']
        else:
            parse['location_user'] = None
    else:
        parse['location_user'] = rough_json['lbs']['idname']
    if rough_json['lbs']['idname'] == '':
        if 'story_info' in rough_json:
            parse['location_real'] = rough_json['story_info']['lbs']['name']
        else:
            parse['location_real'] = None
    else:
        parse['location_real'] = rough_json['lbs']['idname']
    if rough_json['lbs']['pos_x'] == '':
        if 'story_info' in rough_json:
            parse['longitude'] = rough_json['story_info']['lbs']['pos_x']
        else:
            parse['longitude'] = None
    else:
        parse['longitude'] = rough_json['lbs']['pos_x']
    if rough_json['lbs']['pos_y'] == '':
        if 'story_info' in rough_json:
            parse['latitude'] = rough_json['story_info']['lbs']['pos_y']
        else:
            parse['latitude'] = None
    else:
        parse['latitude'] = rough_json['lbs']['pos_y']
    if 'story_info' in rough_json:
        parse['photo_time'] = rough_json['story_info']['time']
    else:
        parse['photo_time'] = None
    parse['commentnum'] = rough_json['cmtnum']
    logger.info('解析tid为 %s 的说说粗数据成功' % parse['tid'])
    logger.debug('解析得到的Python形式的JSON为 %s' % parse)
    return parse