#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Parse JSON of Qzone """

__author__ = 'Ding Junyao'

import logging
import csv
import os
from qzone_spider import svar
import re

logger = logging.getLogger(__name__)


def emotion_parse(content):
    with open(os.path.dirname(__file__) + '/emotion.csv', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        emotion_list = list(reader)
    for i in range(len(emotion_list)):
        content = content.replace(emotion_list[i]['code'], emotion_list[i]['symbol'])
    return content


def rough_json_parse(rough_json_list, ordernum, catch_time=0):
    rough_json = rough_json_list[ordernum]
    parse = {'catch_time': catch_time, 'tid': rough_json['tid'], 'qq': rough_json['uin'],
             'post_time': rough_json['created_time'], 'commentnum': rough_json['cmtnum']}
    if svar.emotionParse:
        parse['name'] = emotion_parse(rough_json['name'])
    else:
        parse['name'] = rough_json['name']
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
    # TODO：分享链接
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
    if rough_json['commentlist'] is None:
        parse['comment'] = None
    else:
        parse['comment'] = []
        for comment in rough_json['commentlist']:
            one_comment = {'commentid': comment['tid'], 'qq': comment['uin'],
                           'post_time': comment['create_time'], 'replynum': comment['reply_num']}
            if svar.emotionParse:
                one_comment['name'] = emotion_parse(comment['name'])
            else:
                one_comment['name'] = comment['name']
            if 'content' in comment and comment['content'] != '':
                if svar.emotionParse:
                    one_comment['content'] = emotion_parse(comment['content'])
                else:
                    one_comment['content'] = comment['content']
            else:
                one_comment['content'] = None
            if 'pictotal' in comment:
                one_comment['picnum'] = comment['pictotal']
                one_comment['pic'] = []
                for pic in comment['pic']:
                    one_pic = {'url': pic['b_url'], 'thumb': pic['s_url']}
                    one_comment['pic'].append(one_pic)
            else:
                one_comment['picnum'] = 0
                one_comment['pic'] = None
            if 'list_3' in comment:
                one_comment['reply'] = []
                for reply in comment['list_3']:
                    one_reply = {'replyid': reply['tid'], 'qq': reply['uin'], 'name': reply['name'],
                                 'post_time': reply['create_time']}
                    replyinfo = re.search(r'@{uin:([1-9][0-9]{4,}),nick:(.*),who:1,auto:1}(.*)', reply['content'])
                    one_reply['reply_target_qq'] = replyinfo.group(1)
                    if svar.emotionParse:
                        one_reply['reply_target_name'] = emotion_parse(replyinfo.group(2))
                        one_reply['content'] = emotion_parse(replyinfo.group(3))
                    else:
                        one_reply['reply_target_name'] = replyinfo.group(2)
                        one_reply['content'] = replyinfo.group(3)
                    one_comment['reply'].append(one_reply)
            else:
                one_comment['reply'] = None
            parse['comment'].append(one_comment)
    logger.info('Successfully parse rough data of message which tid is %s' % parse['tid'])
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
            content = emotion_parse(msgdata['cell_summary']['summary'])
        else:
            content = msgdata['cell_summary']['summary']
        if 'cell_permission' in msgdata:
            if msgdata['cell_permission']['cell_permission_info'] == '仅自己可见':
                content = content[0:content.rfind('[仅自己可见]')]
        parse['content'] = content
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
    # TODO：点赞、转发、评论
    logger.info('Successfully parse fine data of message which tid is %s' % parse['tid'])
    logger.debug('Returned JSON in Python format is %s' % parse)
    return parse
