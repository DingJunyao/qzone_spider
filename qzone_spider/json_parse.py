#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Parse JSON of Qzone """

__author__ = 'Ding Junyao'

import logging
import csv
import os
from qzone_spider import svar

logger = logging.getLogger(__name__)


def emotion_parse(content):
    print(os.path.dirname(__file__))
    with open(os.path.dirname(__file__) + '/emotion.csv', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        emotion_list = list(reader)
    for i in range(len(emotion_list)):
        content = content.replace(emotion_list[i]['code'], emotion_list[i]['symbol'])
    return content


def rough_json_parse(rough_json_list, ordernum, catch_time=0):
    rough_json = rough_json_list[ordernum]
    parse = {'catch_time': catch_time, 'tid': rough_json['tid'], 'qq': rough_json['uin'],
             'post_time': rough_json['created_time']}
    if 'rt_tid' in rough_json:
        parse['rt_tid'] = rough_json['rt_tid']
    else:
        parse['rt_tid'] = None
    if 'content' in rough_json and rough_json['content'] != '':
        if svar.emotionParse:
            parse['content'] = emotion_parse(rough_json['content'])
        else:
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
    parse['sharelink'] = None
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
    # logger.info('解析tid为 %s 的说说粗数据成功' % parse['tid'])
    logger.info('Successfully parse rough data of message which tid is %s' % parse['tid'])
    # logger.debug('解析得到的Python形式的JSON为 %s' % parse)
    logger.debug('Returned JSON in Python format is %s' % parse)
    return parse


def fine_json_parse(rough_json_list, ordernum, fine_json, catch_time=0):
    # catch_time是细JSON的抓取时间戳
    rough_json = rough_json_list[ordernum]
    msgdata = fine_json['data']
    parse = {'catch_time': catch_time, 'tid': rough_json['tid'], 'qq': rough_json['uin'],
             'post_time': rough_json['created_time']}
    if 'rt_tid' in rough_json:
        parse['rt_tid'] = rough_json['rt_tid']
    else:
        parse['rt_tid'] = None
    if 'content' in rough_json and rough_json['content'] != '':
        if svar.emotionParse:
            parse['content'] = emotion_parse(rough_json['content'])
        else:
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
            picurl = msgdata['cell_pic']['picdata'][i]['photourl']['1']['url']
            picurl = picurl[:picurl.find('&')]
            picthumb = msgdata['cell_pic']['picdata'][i]['photourl']['11']['url']
            picthumb = picthumb[:picthumb.find('&')]
            pic['url'] = picurl
            pic['thumb'] = picthumb
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
            videothumb = msgdata['cell_video']['coverurl']['0']['url']
            videothumb = videothumb[:videothumb.find('&')]
            parse['video'] = {}
            parse['video']['url'] = msgdata['cell_video']['videourl']
            parse['video']['thumb'] = videothumb
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
    parse['sharelink'] = None
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
    # logger.info('解析tid为 %s 的说说细数据成功' % parse['tid'])
    logger.info('Successfully parse fine data of message which tid is %s' % parse['tid'])
    # logger.debug('解析得到的Python形式的JSON为 %s' % parse)
    logger.debug('Returned JSON in Python format is %s' % parse)
    return parse

if __name__ == '__main__':
    print(emotion_parse('【询问[em]e400197[/em]出售[em]e401148[/em]表白】明天早上又要迎来新新的上学日啦～[em]e400116[/em]'))