from flask import Flask
from flask import request
from flask import json
import pymysql
from qzone_spider import svar
from flask import current_app
import datetime
import logging

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


@app.route('/', methods=['GET'])
def intro():
    return 'Hello World'


@app.route('/message_info/<tid>/all', methods=['GET'])
def message_info_all(tid):
    conn = pymysql.connect(host=svar.dbURL, port=svar.dbPort, user=svar.dbUsername, passwd=svar.dbPassword,
                           db=svar.dbDatabase, charset="utf8", use_unicode=True)
    # logger.info('成功连接至在 %s:%s 的 %s 数据库 %s' % (svar.dbURL, svar.dbPort, svar.dbType, svar.dbDatabase))
    app.logger.info('Successfully connect to %s database %s at %s:%s'
                % (svar.dbType, svar.dbDatabase, svar.dbURL, svar.dbPort))
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute('SELECT * FROM message WHERE tid = %s', tid)
    values = cursor.fetchall()
    app.logger.debug(values)
    values_json = []
    media_info = []
    for i in range(len(values)):
        values_json_one = {'catch_time': int(values[i]['catch_time'].timestamp()), 'tid': values[i]['tid'],
                           'qq': values[i]['qq'], 'post_time': int(values[i]['post_time'].timestamp()),
                           'rt_tid': values[i]['rt_tid'], 'content': values[i]['content'],
                           'picnum': values[i]['picnum'], 'videonum': values[i]['videonum'],
                           'sharelink': values[i]['sharelink'], 'device': values[i]['device'],
                           'location_user': values[i]['location_user'], 'location_real': values[i]['location_real'],
                           'longitude': values[i]['longitude'], 'latitude': values[i]['latitude'],
                           'altitude': values[i]['altitude'], 'viewnum': values[i]['viewnum'],
                           'likenum': values[i]['likenum'], 'forwardnum': values[i]['forwardnum'],
                           'commentnum': values[i]['commentnum']}
        if values[i]['photo_time'] is None:
            values_json_one['photo_time'] = None
        else:
            values_json_one['photo_time'] = int(values[i]['photo_time'].timestamp())
        # TODO: 需要简化流程，对于已经查询到的字符串进行缓存，减少查询次数。

        if values[i]['piclist'] is None:
            values_json_one['piclist'] = None
        else:
            piclist_json = []
            for media_id in eval(values[i]['piclist']):
                for store in media_info:
                    if store['id'] == media_id:
                        pic_values = store
                        app.logger.debug('Use stored info')
                        break
                else:
                    cursor.execute('SELECT * FROM media WHERE id = %s', media_id)
                    pic_values = cursor.fetchone()
                    media_info.append(pic_values)
                pic_json = {'url': pic_values['url'], 'thumb': pic_values['thumb']}
                if pic_values['type'] == 'pic_video':
                    pic_json['isvideo'] = 1
                else:
                    pic_json['isvideo'] = 0
                piclist_json.append(pic_json)
            values_json_one['piclist'] = piclist_json
        if values[i]['video'] is None:
            values_json_one['video'] = None
        else:
            for store in media_info:
                if store['id'] == eval(values[i]['video']):
                    video_values = store
                    app.logger.debug('Use stored info')
                    break
            else:
                cursor.execute('SELECT * FROM media WHERE id = %s', eval(values[i]['video']))
                video_values = cursor.fetchone()
                media_info.append(video_values)
            values_json_one['video'] = {'url': video_values['url'], 'thumb': video_values['thumb'], 'time': video_values['time']}
        if values[i]['voice'] is None:
            values_json_one['voice'] = None
        else:
            for store in media_info:
                if store['id'] == eval(values[i]['voice']):
                    voice_values = store
                    app.logger.debug('Use stored info')
                    break
            else:
                cursor.execute('SELECT * FROM media WHERE id = %s', eval(values[i]['voice']))
                voice_values = cursor.fetchone()
                media_info.append(voice_values)
            values_json_one['voice'] = {'url': voice_values['url'], 'time': voice_values['time']}
        values_json.append(values_json_one)
    cursor.close()
    conn.close()
    return json.jsonify(values_json)


@app.route('/message_info/<tid>/latest', methods=['GET'])
def message_info_latest(tid):
    conn = pymysql.connect(host=svar.dbURL, port=svar.dbPort, user=svar.dbUsername, passwd=svar.dbPassword,
                           db=svar.dbDatabase, charset="utf8", use_unicode=True)
    # logger.info('成功连接至在 %s:%s 的 %s 数据库 %s' % (svar.dbURL, svar.dbPort, svar.dbType, svar.dbDatabase))
    app.logger.info('Successfully connect to %s database %s at %s:%s'
                % (svar.dbType, svar.dbDatabase, svar.dbURL, svar.dbPort))
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute('select * from message where tid = %s order by catch_time desc limit 1;', tid)
    values = cursor.fetchone()
    app.logger.debug(values)
    media_info = []
    values_json = {'catch_time': int(values['catch_time'].timestamp()), 'tid': values['tid'],
                   'qq': values['qq'], 'post_time': int(values['post_time'].timestamp()),
                   'rt_tid': values['rt_tid'], 'content': values['content'],
                   'picnum': values['picnum'], 'videonum': values['videonum'],
                   'sharelink': values['sharelink'], 'device': values['device'],
                   'location_user': values['location_user'], 'location_real': values['location_real'],
                   'longitude': values['longitude'], 'latitude': values['latitude'],
                   'altitude': values['altitude'], 'viewnum': values['viewnum'],
                   'likenum': values['likenum'], 'forwardnum': values['forwardnum'],
                   'commentnum': values['commentnum']}
    if values['photo_time'] is None:
        values_json['photo_time'] = None
    else:
        values_json['photo_time'] = int(values['photo_time'].timestamp())
    # TODO: 需要简化流程，对于已经查询到的字符串进行缓存，减少查询次数。

    if values['piclist'] is None:
        values_json['piclist'] = None
    else:
        piclist_json = []
        for media_id in eval(values['piclist']):
            for store in media_info:
                if store['id'] == media_id:
                    pic_values = store
                    app.logger.debug('Use stored info')
                    break
            else:
                cursor.execute('SELECT * FROM media WHERE id = %s', media_id)
                pic_values = cursor.fetchone()
                media_info.append(pic_values)
            pic_json = {'url': pic_values['url'], 'thumb': pic_values['thumb']}
            if pic_values['type'] == 'pic_video':
                pic_json['isvideo'] = 1
            else:
                pic_json['isvideo'] = 0
            piclist_json.append(pic_json)
        values_json['piclist'] = piclist_json
    if values['video'] is None:
        values_json['video'] = None
    else:
        for store in media_info:
            if store['id'] == eval(values['video']):
                video_values = store
                app.logger.debug('Use stored info')
                break
        else:
            cursor.execute('SELECT * FROM media WHERE id = %s', eval(values['video']))
            video_values = cursor.fetchone()
            media_info.append(video_values)
        values_json['video'] = {'url': video_values['url'], 'thumb': video_values['thumb'], 'time': video_values['time']}
    if values['voice'] is None:
        values_json['voice'] = None
    else:
        for store in media_info:
            if store['id'] == eval(values['voice']):
                voice_values = store
                app.logger.debug('Use stored info')
                break
        else:
            cursor.execute('SELECT * FROM media WHERE id = %s', eval(values['voice']))
            voice_values = cursor.fetchone()
            media_info.append(voice_values)
        values_json['voice'] = {'url': voice_values['url'], 'time': voice_values['time']}
    cursor.close()
    conn.close()
    return json.jsonify(values_json)


if __name__ == '__main__':
    app.debug = True
    app.run()
