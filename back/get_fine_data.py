#!/usr/bin/env python3
import logging
import requests
import json
import time
from qzone_spider import svar
'''
get_fine_data.py

Author: Ding Junyao

Usage: get_fine_data(qq, tid, cookie, gtk, qzonetoken)

Return:
If success:
If failed: '-1'
'''

logger = logging.getLogger(__name__)


def get_fine_json(qq, tid, cookie, gtk, qzonetoken):
    fail = 0
    while fail < svar.getFineDataFailTime:
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
        response_msg = s.request('GET', svar.fineJSON_URL, params=params_msg, headers=svar.requestHeader, cookies=cookie)
        if (response_msg.status_code == 200) & (response_msg.text is not None):
            response_msg_text = response_msg.text  # 读取响应内容
            # print(response_msg_text)
            response_msg_json = json.loads(response_msg_text)
            if response_msg_json['ret'] >= 0:
                logger.info('获取QQ为 %s 的tid为 %s 的说说数据成功' % (qq, tid))
                logger.debug('返回的Python形式的JSON为 %s' % json.dumps(response_msg_json, ensure_ascii=False, indent=2))
                return catch_time, response_msg_json
            else:
                fail += 1
                if fail == svar.getFineDataFailTime:
                    break
                logger.warning('获取QQ为 %s 的tid为 %s 的说说数据时返回异常，休息 %s 秒后继续，剩余重试次数为: %s' % (qq, tid, svar.errorWaitTime, svar.getFineDataFailTime - fail))
                logger.debug('返回的Python形式的JSON为 %s' % response_msg_json)
                time.sleep(svar.errorWaitTime)
        else:
            fail += 1
            if fail == svar.getFineDataFailTime:
                break
            logger.warning('获取QQ为 %s 的tid为 %s 的说说数据时请求失败，休息 %s 秒后继续，剩余重试次数为: %s' % (qq, tid, svar.errorWaitTime, svar.getFineDataFailTime - fail))
            logger.debug('HTTP状态码为 %s' % response_msg.status_code)
            time.sleep(svar.errorWaitTime)
    logger.error('获取QQ为 %s 的tid为 %s 的说说数据失败' % (qq, tid))
    return 0, -1


def fine_json_parse(rough_json_set, ordernum, fine_json, catch_time=0):
    # TODO: 这里面有一些值不一定在所有的JSON里面有，需要提前判断。默认使用粗JSON，但评论数除外。
    # TODO: 记录关于媒体的详细信息，如视频时间、观看人数。还有QQ、评论的记录。
    # catch_time是细JSON的抓取时间戳
    rough_json = rough_json_set[ordernum]
    msgdata = fine_json['data']
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
    if 'cell_pic' in msgdata:
        parse['piclist'] = []
        for i in range(len(msgdata['cell_pic']['picdata'])):
            pic = {}
            pic['url'] = msgdata['cell_pic']['picdata'][i]['photourl']['1']['url']
            pic['thumb'] = msgdata['cell_pic']['picdata'][i]['photourl']['11']['url']
            pic['isvideo'] = msgdata['cell_pic']['picdata'][i]['videoflag']
            parse['piclist'].append(pic)
    else:
        parse['piclist'] = None
    if 'videototal' in rough_json and 'rt_tid' not in rough_json:
        parse['videonum'] = rough_json['videototal']
    else:
        parse['videonum'] = 0
    if 'videototal' in rough_json and 'rt_tid' not in rough_json:
        if rough_json['videototal'] != 0:
            parse['video'] = {}
            parse['video']['url'] = msgdata['cell_video']['videourl']
            parse['video']['thumb'] = msgdata['cell_video']['coverurl']['0']['url']
            parse['video']['time'] = msgdata['cell_video']['videotime']
        else:
            parse['video'] = None
    else:
        parse['video'] = None
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
    if 'cell_visitor' in msgdata:
        parse['viewnum'] = msgdata['cell_visitor']['view_count']
    else:
        parse['viewnum'] = 0
    if 'cell_like' in msgdata:
        parse['likenum'] = msgdata['cell_like']['num']
    else:
        parse['likenum'] = 0
    parse['forwardnum'] = msgdata['cell_forward_list']['num']
    if 'cell_comment' in msgdata:
        parse['commentnum'] = msgdata['cell_comment']['num']
    else:
        parse['commentnum'] = 0
    logger.info('解析tid为 %s 的说说细数据成功' % parse['tid'])
    logger.debug('解析得到的Python形式的JSON为 %s' % parse)
    return parse
