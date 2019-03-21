#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Parse JSON of Qzone """

__author__ = 'Ding Junyao'

import logging
import csv
import os
import re

logger = logging.getLogger(__name__)


def emotion_parse(content):
    emofile = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'emotion.csv')
    with open(emofile, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        emotion_list = list(reader)
    for i in range(len(emotion_list)):
        content = content.replace(emotion_list[i]['code'], emotion_list[i]['symbol'])
    return content


def rough_json_parse(rough_json_list, ordernum, catch_time=0, do_emotion_parse=True):
    rough_json = rough_json_list[ordernum]
    parse = {'catch_time': catch_time, 'tid': rough_json['tid'], 'qq': rough_json['uin'],
             'post_time': rough_json['created_time'], 'commentnum': rough_json['cmtnum']}
    if do_emotion_parse:
        parse['name'] = emotion_parse(rough_json['name'])
    else:
        parse['name'] = rough_json['name']
    if 'content' in rough_json and rough_json['content'] != '':
        if do_emotion_parse:
            parse['content'] = emotion_parse(rough_json['content'])
        else:
            parse['content'] = rough_json['content']
    else:
        parse['content'] = None
    if 'rt_tid' in rough_json:
        parse['rt'] = {'tid': rough_json['rt_tid'], 'qq': rough_json['rt_uin']}
        if do_emotion_parse:
            parse['rt']['name'] = emotion_parse(rough_json['rt_uinname'])
        else:
            parse['rt']['name'] = rough_json['rt_uinname']
        if 'rt_con' in rough_json and rough_json['rt_con']['content'] != '':
            if do_emotion_parse:
                parse['rt']['content'] = emotion_parse(rough_json['rt_con']['content'])
            else:
                parse['rt']['content'] = rough_json['rt_con']['content']
        else:
            parse['rt']['content'] = None
        if 'rt_source_name' in rough_json and rough_json['rt_source_name'] != '':
            parse['rt']['device'] = rough_json['rt_source_name']
        else:
            parse['rt']['device'] = None
        if 'pictotal' in rough_json:
            parse['rt']['picnum'] = rough_json['pictotal']
            parse['rt']['piclist'] = []
            if 'pic' in rough_json and rough_json['pic']:
                for one_pic in rough_json['pic']:
                    pic = {}
                    if 'is_video' in one_pic and one_pic['is_video'] == 1 and 'video_info' in one_pic:
                        pic['url'] = one_pic['video_info']['url3']
                        pic['thumb'] = one_pic['video_info']['url1']
                        pic['isvideo'] = 1
                    else:
                        pic['url'] = one_pic['url1']
                        pic['thumb'] = one_pic['url3']
                        pic['isvideo'] = 0
                    parse['rt']['piclist'].append(pic)
            else:
                parse['rt']['piclist'] = None
        else:
            parse['rt']['picnum'] = 0
            parse['rt']['piclist'] = None
        if 'videototal' in rough_json and 'video' in rough_json and rough_json['video']:
            parse['rt']['video'] = {'url': rough_json['video'][0]['url3'], 'thumb': rough_json['video'][0]['url1']}
        else:
            parse['rt']['video'] = None
        if rough_json['lbs']['idname'] == '':
            if 'story_info' in rough_json:
                parse['rt']['location_user'] = rough_json['story_info']['lbs']['idname']
            else:
                parse['rt']['location_user'] = None
        else:
            parse['rt']['location_user'] = rough_json['lbs']['idname']
        if rough_json['lbs']['idname'] == '':
            if 'story_info' in rough_json:
                parse['rt']['location_real'] = rough_json['story_info']['lbs']['name']
            else:
                parse['rt']['location_real'] = None
        else:
            parse['rt']['location_real'] = rough_json['lbs']['idname']
        if rough_json['lbs']['pos_x'] == '':
            if 'story_info' in rough_json:
                parse['rt']['longitude'] = rough_json['story_info']['lbs']['pos_x']
            else:
                parse['rt']['longitude'] = None
        else:
            parse['rt']['longitude'] = rough_json['lbs']['pos_x']
        if rough_json['lbs']['pos_y'] == '':
            if 'story_info' in rough_json:
                parse['rt']['latitude'] = rough_json['story_info']['lbs']['pos_y']
            else:
                parse['rt']['latitude'] = None
        else:
            parse['rt']['latitude'] = rough_json['lbs']['pos_y']
        if 'story_info' in rough_json:
            parse['rt']['photo_time'] = rough_json['story_info']['time']
        else:
            parse['rt']['photo_time'] = None
        parse['picnum'] = 0
        parse['piclist'] = None
        parse['video'] = None
        parse['voice'] = None
        parse['location_user'] = None
        parse['location_real'] = None
        parse['longitude'] = None
        parse['latitude'] = None
        parse['photo_time'] = None
    else:
        parse['rt'] = None
        if 'pictotal' in rough_json:
            parse['picnum'] = rough_json['pictotal']
            parse['piclist'] = []
            if 'pic' in rough_json and rough_json['pic']:
                for one_pic in rough_json['pic']:
                    pic = {}
                    if 'is_video' in one_pic and one_pic['is_video'] == 1 and 'video_info' in one_pic:
                        pic['url'] = one_pic['video_info']['url3']
                        pic['thumb'] = one_pic['video_info']['url1']
                        pic['isvideo'] = 1
                    else:
                        pic['url'] = one_pic['url1']
                        pic['thumb'] = one_pic['url3']
                        pic['isvideo'] = 0
                    parse['piclist'].append(pic)
            else:
                parse['piclist'] = None
        else:
            parse['picnum'] = 0
            parse['piclist'] = None
        if 'videototal' in rough_json and 'video' in rough_json and rough_json['video']:
            parse['video'] = {'url': rough_json['video'][0]['url3'], 'thumb': rough_json['video'][0]['url1']}
        else:
            parse['video'] = None
        if 'voice' in rough_json:
            parse['voice'] = {'url': rough_json['voice'][0]['url'], 'time': rough_json['voice'][0]['time']}
        else:
            parse['voice'] = None
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
    parse['sharelink'] = None
    if 'source_name' in rough_json and rough_json['source_name'] != '':
        parse['device'] = rough_json['source_name']
    else:
        parse['device'] = None
    if 'commentlist' in rough_json and rough_json['commentlist']:
        parse['comment'] = []
        for comment in rough_json['commentlist']:
            one_comment = {'commentid': comment['tid'], 'qq': comment['uin'],
                           'post_time': comment['create_time'], 'replynum': comment['reply_num']}
            if do_emotion_parse:
                one_comment['name'] = emotion_parse(comment['name'])
            else:
                one_comment['name'] = comment['name']
            if 'content' in comment and comment['content'] != '':
                if do_emotion_parse:
                    one_comment['content'] = emotion_parse(comment['content'])
                else:
                    one_comment['content'] = comment['content']
            else:
                one_comment['content'] = None
            if 'pictotal' in comment:
                one_comment['picnum'] = comment['pictotal']
                one_comment['piclist'] = []
                for pic in comment['pic']:
                    one_pic = {'url': pic['b_url'], 'thumb': pic['s_url']}
                    one_comment['piclist'].append(one_pic)
            else:
                one_comment['picnum'] = 0
                one_comment['piclist'] = None
            if 'list_3' in comment:
                one_comment['reply'] = []
                for reply in comment['list_3']:
                    one_reply = {'replyid': reply['tid'], 'qq': reply['uin'], 'post_time': reply['create_time']}
                    replyinfo = re.search(r'@{uin:([1-9][0-9]{4,}),nick:(.*),who:1,auto:1}(.*)', reply['content'])
                    one_reply['reply_target_qq'] = replyinfo.group(1)
                    if do_emotion_parse:
                        one_reply['name'] = emotion_parse(reply['name'])
                        one_reply['reply_target_name'] = emotion_parse(replyinfo.group(2))
                        one_reply['content'] = emotion_parse(replyinfo.group(3))
                    else:
                        one_reply['name'] = reply['name']
                        one_reply['reply_target_name'] = replyinfo.group(2)
                        one_reply['content'] = replyinfo.group(3)
                    one_comment['reply'].append(one_reply)
            else:
                one_comment['reply'] = None
            parse['comment'].append(one_comment)
    else:
        parse['comment'] = None
    logger.info('Successfully parse rough data of message which tid is %s' % parse['tid'])
    logger.debug('Returned JSON in Python format is %s' % parse)
    return parse


def fine_json_parse(rough_json_list, ordernum, fine_json, catch_time=0, do_emotion_parse=True):
    rough_json = rough_json_list[ordernum]
    msgdata = fine_json['data']
    parse = {'catch_time': catch_time, 'tid': rough_json['tid'], 'qq': rough_json['uin'],
             'post_time': rough_json['created_time']}
    if do_emotion_parse:
        parse['name'] = emotion_parse(rough_json['name'])
    else:
        parse['name'] = rough_json['name']
    if 'rt_tid' in rough_json:
        parse['rt'] = {'tid': rough_json['rt_tid'], 'post_time': msgdata['cell_original']['cell_comm']['time'],
                       'qq': rough_json['rt_uin']}
        if do_emotion_parse:
            parse['rt']['name'] = emotion_parse(rough_json['rt_uinname'])
        else:
            parse['rt']['name'] = rough_json['rt_uinname']
        if 'rt_con' in rough_json and rough_json['rt_con']['content'] != '':
            if do_emotion_parse:
                parse['rt']['content'] = emotion_parse(msgdata['cell_original']['cell_summary']['summary'])
            else:
                parse['rt']['content'] = msgdata['cell_original']['cell_summary']['summary']
        else:
            parse['rt']['content'] = None
        if 'rt_source_name' in rough_json and rough_json['rt_source_name'] != '':
            parse['rt']['device'] = rough_json['rt_source_name']
        else:
            parse['rt']['device'] = None
        if 'pictotal' in rough_json:
            parse['rt']['picnum'] = rough_json['pictotal']
        else:
            parse['rt']['picnum'] = 0
        if 'cell_pic' in msgdata['cell_original']:
            parse['rt']['piclist'] = []
            for one_pic in msgdata['cell_original']['cell_pic']['picdata']:
                pic = {}
                picurl = one_pic['photourl']['1']['url']
                picurl = picurl[:picurl.find('&')]
                picthumb = one_pic['photourl']['11']['url']
                picthumb = picthumb[:picthumb.find('&')]
                pic['url'] = picurl
                pic['thumb'] = picthumb
                pic['isvideo'] = one_pic['videoflag']
                parse['rt']['piclist'].append(pic)
        else:
            parse['rt']['piclist'] = None
        if 'videototal' in rough_json and rough_json['videototal'] != 0:
            videothumb = msgdata['cell_original']['cell_video']['coverurl']['0']['url']
            videothumb = videothumb[:videothumb.find('&')]
            parse['rt']['video'] = {'url': msgdata['cell_original']['cell_video']['videourl'], 'thumb': videothumb,
                                    'time': msgdata['cell_original']['cell_video']['videotime']}
        else:
            parse['rt']['video'] = None
        if rough_json['lbs']['idname'] == '':
            if 'story_info' in rough_json:
                parse['rt']['location_user'] = rough_json['story_info']['lbs']['idname']
            else:
                parse['rt']['location_user'] = None
        else:
            parse['rt']['location_user'] = rough_json['lbs']['idname']
        if rough_json['lbs']['idname'] == '':
            if 'story_info' in rough_json:
                parse['rt']['location_real'] = rough_json['story_info']['lbs']['name']
            else:
                parse['rt']['location_real'] = None
        else:
            parse['rt']['location_real'] = rough_json['lbs']['idname']
        if rough_json['lbs']['pos_x'] == '':
            if 'story_info' in rough_json:
                parse['rt']['longitude'] = rough_json['story_info']['lbs']['pos_x']
            else:
                parse['rt']['longitude'] = None
        else:
            parse['rt']['longitude'] = rough_json['lbs']['pos_x']
        if rough_json['lbs']['pos_y'] == '':
            if 'story_info' in rough_json:
                parse['rt']['latitude'] = rough_json['story_info']['lbs']['pos_y']
            else:
                parse['rt']['latitude'] = None
        else:
            parse['rt']['latitude'] = rough_json['lbs']['pos_y']
        if 'story_info' in rough_json:
            parse['rt']['photo_time'] = rough_json['story_info']['time']
        else:
            parse['rt']['photo_time'] = None
        parse['picnum'] = 0
        parse['piclist'] = None
        parse['video'] = None
        parse['voice'] = None
        parse['location_user'] = None
        parse['location_real'] = None
        parse['longitude'] = None
        parse['latitude'] = None
        parse['photo_time'] = None
    else:
        parse['rt'] = None
        if 'pictotal' in rough_json:
            parse['picnum'] = rough_json['pictotal']
        else:
            parse['picnum'] = 0
        if 'cell_pic' in msgdata:
            parse['piclist'] = []
            for one_pic in msgdata['cell_pic']['picdata']:
                picurl = one_pic['photourl']['1']['url']
                picurl = picurl[:picurl.find('&')]
                picthumb = one_pic['photourl']['11']['url']
                picthumb = picthumb[:picthumb.find('&')]
                pic = {'url': picurl, 'thumb': picthumb, 'isvideo': one_pic['videoflag']}
                parse['piclist'].append(pic)
        else:
            parse['piclist'] = None
        if 'videototal' in rough_json and rough_json['videototal'] != 0:
            videothumb = msgdata['cell_video']['coverurl']['0']['url']
            videothumb = videothumb[:videothumb.find('&')]
            parse['video'] = {'url': msgdata['cell_video']['videourl'], 'thumb': videothumb,
                              'time': msgdata['cell_video']['videotime']}
        else:
            parse['video'] = None
        if 'voice' in rough_json:
            parse['voice'] = {'url': rough_json['voice'][0]['url'], 'time': rough_json['voice'][0]['time']}
        else:
            parse['voice'] = None
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
    if 'content' in rough_json and rough_json['content'] != '':
        if do_emotion_parse:
            content = emotion_parse(msgdata['cell_summary']['summary'])
        else:
            content = msgdata['cell_summary']['summary']
        if 'cell_permission' in msgdata:
            if 'cell_permission_info' in msgdata['cell_permission'] and \
                    msgdata['cell_permission']['cell_permission_info'] == '仅自己可见':
                content = content[0:content.rfind('[仅自己可见]')]
        parse['content'] = content
    else:
        parse['content'] = None
    if 'source_name' in rough_json and rough_json['source_name'] != '':
        parse['device'] = rough_json['source_name']
    else:
        parse['device'] = None
    if 'cell_visitor' in msgdata:
        parse['viewnum'] = msgdata['cell_visitor']['view_count']
    else:
        parse['viewnum'] = 0
    if 'cell_like' in msgdata:
        parse['likenum'] = msgdata['cell_like']['num']
        if 'likemans' in msgdata['cell_like'] and msgdata['cell_like']['likemans']:
            parse['like'] = []
            for likeman in msgdata['cell_like']['likemans']:
                one_likeman = {'qq': likeman['user']['uin']}
                if do_emotion_parse:
                    one_likeman['name'] = emotion_parse(likeman['user']['nickname'])
                else:
                    one_likeman['name'] = likeman['user']['nickname']
                parse['like'].append(one_likeman)
        else:
            parse['like'] = None
    else:
        parse['likenum'] = 0
        parse['like'] = None
    parse['forwardnum'] = msgdata['cell_forward_list']['num']
    if msgdata['cell_forward_list']['fwdmans']:
        parse['forward'] = []
        for forwardman in msgdata['cell_forward_list']['fwdmans']:
            one_forward = {'qq': forwardman['uin']}
            if do_emotion_parse:
                one_forward['name'] = emotion_parse(forwardman['nickname'])
            else:
                one_forward['name'] = forwardman['nickname']
            parse['forward'].append(one_forward)
    else:
        parse['forward'] = None
    if 'cell_comment' in msgdata:
        parse['commentnum'] = msgdata['cell_comment']['num']
        parse['comment'] = []
        for comment in msgdata['cell_comment']['comments']:
            one_comment = {'commentid': int(comment['commentid']), 'qq': comment['user']['uin'],
                           'post_time': comment['date'], 'replynum': comment['replynum'], 'likenum': comment['likeNum']}
            if do_emotion_parse:
                one_comment['name'] = emotion_parse(comment['user']['nickname'])
            else:
                one_comment['name'] = comment['user']['nickname']
            if 'content' in comment and comment['content'] != '':
                if do_emotion_parse:
                    one_comment['content'] = emotion_parse(comment['content'])
                else:
                    one_comment['content'] = comment['content']
            else:
                one_comment['content'] = None
            if 'commentpic' in comment and comment['commentpic']:
                one_comment['picnum'] = len(comment['commentpic'])
                one_comment['piclist'] = []
                for pic in comment['commentpic']:
                    one_pic = {'url': pic['photourl']['1']['url'], 'thumb': pic['photourl']['11']['url']}
                    one_comment['piclist'].append(one_pic)
            else:
                one_comment['picnum'] = 0
                one_comment['piclist'] = None
            if 'likemans' in comment and comment['likemans']:
                one_comment['like'] = []
                for likeman in comment['likemans']:
                    one_comment_likeman = {'qq': likeman['user']['uin']}
                    if do_emotion_parse:
                        one_comment_likeman['name'] = emotion_parse(likeman['user']['nickname'])
                    else:
                        one_comment_likeman['name'] = likeman['nickname']
                    one_comment['like'].append(one_comment_likeman)
            else:
                one_comment['like'] = None
            if 'replys' in comment and comment['replys']:
                one_comment['reply'] = []
                for reply in comment['replys']:
                    one_reply = {'replyid': reply['replyid'], 'qq': reply['user']['uin'],
                                 'name': reply['user']['nickname'], 'post_time': reply['date'],
                                 'reply_target_qq': reply['target']['uin']}
                    if do_emotion_parse:
                        one_reply['reply_target_name'] = emotion_parse(reply['target']['nickname'])
                        one_reply['content'] = emotion_parse(reply['content'])
                    else:
                        one_reply['reply_target_name'] = reply['target']['nickname']
                        one_reply['content'] = reply['content']
                    one_comment['reply'].append(one_reply)
            else:
                one_comment['reply'] = None
            parse['comment'].append(one_comment)
    else:
        parse['commentnum'] = 0
        parse['comment'] = None
    logger.info('Successfully parse fine data of message which tid is %s' % parse['tid'])
    logger.debug('Returned JSON in Python format is %s' % parse)
    return parse
