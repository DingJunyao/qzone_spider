#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" MySQL connection and insert of qzone_spider """

__author__ = 'Ding Junyao'

import pymysql
import logging

logger = logging.getLogger(__name__)

create_table_sql = (
    '''CREATE TABLE `user_loginfo` (
        `uid` INT(11) NOT NULL AUTO_INCREMENT,
        `email` VARCHAR(127)  NOT NULL,
        `mobile`  INT(11) NOT NULL,
        `password`  VARCHAR(64) NOT NULL,
        `nickname`  VARCHAR(64) DEFAULT NULL,
        PRIMARY KEY (`uid`)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;''',
    '''CREATE TABLE `target` (
        `uid` INT(11) NOT NULL,
        `target_qq` BIGINT(16)  NOT NULL,
        `mode`  INT(1) NOT NULL,
        PRIMARY KEY (`uid`, `target_qq`)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;''',
    '''CREATE TABLE `message` (
        `catch_time` DATETIME NOT NULL,
        `tid` VARCHAR(26) NOT NULL,
        `qq`  BIGINT(16) NOT NULL,
        `post_time`  DATETIME NOT NULL,
        `rt_tid`  VARCHAR(26) DEFAULT NULL,
        `content` TEXT  DEFAULT NULL,
        `picnum`  INT(3)  DEFAULT NULL,
        `piclist` TEXT  DEFAULT NULL,
        `video` TEXT  DEFAULT NULL,
        `voice` TEXT  DEFAULT NULL,
        `device`  VARCHAR(100)  DEFAULT NULL,
        `location_user`  VARCHAR(100)  DEFAULT NULL,
        `location_real`  VARCHAR(100)  DEFAULT NULL,
        `longitude` DOUBLE(11,7)  DEFAULT NULL,
        `latitude` DOUBLE(11,7)  DEFAULT NULL,
        `photo_time`  DATETIME DEFAULT NULL,
        `viewnum` INT(11) DEFAULT NULL,
        `likenum` INT(11) DEFAULT NULL,
        `forwardnum` INT(11) DEFAULT NULL,
        `commentnum` INT(11) DEFAULT NULL,
        PRIMARY KEY (`catch_time`,`tid`)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;''',
    '''CREATE TABLE `rt` (
        `tid` VARCHAR(26) NOT NULL,
        `qq`  BIGINT(16) NOT NULL,
        `post_time`  DATETIME DEFAULT NULL,
        `content` TEXT DEFAULT NULL,
        `picnum`  INT(3)  DEFAULT NULL,
        `piclist` TEXT  DEFAULT NULL,
        `video` TEXT  DEFAULT NULL,
        `device`  VARCHAR(100)  DEFAULT NULL,
        `location_user`  VARCHAR(100)  DEFAULT NULL,
        `location_real`  VARCHAR(100)  DEFAULT NULL,
        `longitude` DOUBLE(11,7)  DEFAULT NULL,
        `latitude` DOUBLE(11,7)  DEFAULT NULL,
        `photo_time`  DATETIME DEFAULT NULL,
        PRIMARY KEY (`tid`)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;''',
    '''CREATE TABLE `like_person`(
        `tid` VARCHAR(26) NOT NULL,
        `commentid` INT(11) DEFAULT NULL,
        `qq`  BIGINT(16) NOT NULL,
        PRIMARY KEY (`tid`,`commentid`,`qq`)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;''',
    '''CREATE TABLE `forward`(
        `tid` VARCHAR(26) NOT NULL,
        `qq`  BIGINT(16) NOT NULL,
        PRIMARY KEY (`tid`,`qq`)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;''',
    '''CREATE TABLE `comment_reply`(
        `catch_time` DATETIME NOT NULL,
        `tid` VARCHAR(26) NOT NULL,
        `commentid` INT(11) NOT NULL,
        `replyid` INT(11) NOT NULL,
        `qq`  BIGINT(16) NOT NULL,
        `reply_target_qq`  BIGINT(16) DEFAULT NULL,
        `post_time`  DATETIME NOT NULL,
        `content` TEXT  DEFAULT NULL,
        `picnum`  INT(2)  DEFAULT NULL,
        `piclist` TEXT  DEFAULT NULL,
        `likenum` INT(11) DEFAULT NULL,
        `replynum` INT(11) DEFAULT NULL,
        PRIMARY KEY (`catch_time`,`tid`,`commentid`,`replyid`)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;''',
    '''CREATE TABLE `media`(
        `id`  INT(11) NOT NULL AUTO_INCREMENT,
        `type`  VARCHAR(15)  NOT NULL,
        `url` VARCHAR(300)  NOT NULL,
        `thumb` VARCHAR(300)  DEFAULT NULL,
        `time` INT(11)  DEFAULT NULL,
        PRIMARY KEY (`id`)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;''',
    'ALTER TABLE `media` ADD UNIQUE `url` (`url`(191));',
    '''CREATE TABLE `qq`(
        `uid`	INT(11)	NOT NULL,
        `qq`  BIGINT(16)  NOT NULL,
        `name`  VARCHAR(64) DEFAULT NULL,
        `memo`  TEXT	DEFAULT NULL,
        PRIMARY KEY (`uid`,`qq`)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;''',
    '''CREATE TABLE `message_memo` (
        `id`	INT(11)	NOT NULL AUTO_INCREMENT,
        `uid`	INT(11)	NOT NULL,
        `tid` VARCHAR(26) NOT NULL,
        `memo`  TEXT	NOT NULL,
        PRIMARY KEY (`id`)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;''',
    '''CREATE TABLE `comment_reply_memo`(
        `id`	INT(11)	NOT NULL AUTO_INCREMENT,
        `uid`	INT(11)	NOT NULL,
        `tid` VARCHAR(26) NOT NULL,
        `commentid` INT(11) NOT NULL,
        `replyid` INT(11) NOT NULL,
        `memo`  TEXT	NOT NULL,
        PRIMARY KEY (`id`)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;''',
    '''CREATE TABLE `media_memo` (
        `id`	INT(11)	NOT NULL AUTO_INCREMENT,
        `uid`	INT(11)	NOT NULL,
        `media_id` INT(11) NOT NULL,
        `memo`  TEXT	NOT NULL,
        PRIMARY KEY (`id`)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;'''
)


def db_init(db_url, db_database, db_username, db_password, db_port=3306):
    conn = pymysql.connect(host=db_url, port=db_port, user=db_username, passwd=db_password,
                           db=db_database, charset="utf8mb4", use_unicode=True)
    logger.info('Successfully connect to MySQL database %s at %s:%s'
                % (db_database, db_url, db_port))
    cursor = conn.cursor()
    for i in create_table_sql:
        cursor.execute(i)
    logger.info('Database initialized')
    cursor.close()
    conn.close()


def db_write_rough(parse, db_url, db_database, db_username, db_password, db_port=3306, uid=1):
    conn = pymysql.connect(host=db_url, port=db_port, user=db_username, passwd=db_password,
                           db=db_database, charset="utf8mb4", use_unicode=True)
    logger.info('Successfully connect to MySQL database %s at %s:%s'
                % (db_database, db_url, db_port))
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    if cursor.execute('SELECT * FROM qq WHERE uid = %s AND qq = %s;', (uid, parse['qq'])) == 0:
        try:
            cursor.execute('INSERT INTO qq(uid, qq, name) VALUES (%s, %s, %s);', (uid, parse['qq'], parse['name']))
            conn.commit()
            logger.info('Successfully insert QQ information of %s in uid %s' % (parse['qq'], uid))
        except Exception:
            logger.error('Error when trying to insert QQ information of %s in uid %s' % (parse['qq'], uid))
    else:
        if cursor.fetchone()['name'] != parse['name']:
            try:
                cursor.execute('UPDATE qq SET name = %s WHERE uid = %s and qq = %s;', (parse['name'], uid, parse['qq']))
                conn.commit()
                logger.info('Successfully update QQ information of %s in uid %s' % (parse['qq'], uid))
            except Exception:
                logger.error('Error when trying to update QQ information of %s in uid %s' % (parse['qq'], uid))
    if parse['rt'] is not None:
        rt = parse['rt']
        rt_tid = rt['tid']
        if cursor.execute('SELECT * FROM qq WHERE uid = %s AND qq = %s;', (uid, rt['qq'])) == 0:
            try:
                cursor.execute('INSERT INTO qq(uid, qq, name) VALUES (%s, %s, %s);',
                               (uid, rt['qq'], rt['name']))
                conn.commit()
                logger.info('Successfully insert QQ information of %s in uid %s' % (rt['qq'], uid))
            except Exception:
                logger.error('Error when trying to insert QQ information of %s in uid %s' % (rt['qq'], uid))
        else:
            if cursor.fetchone()['name'] != rt['name']:
                try:
                    cursor.execute('UPDATE qq SET name = %s WHERE uid = %s and qq = %s;',
                                   (rt['name'], uid, rt['qq']))
                    conn.commit()
                    logger.info('Successfully update QQ information of %s in uid %s' % (rt['qq'], uid))
                except Exception:
                    logger.error('Error when trying to update QQ information of %s in uid %s'
                                 % (rt['qq'], uid))
        if rt['piclist'] is not None:
            rt_pic_id_list = []
            for one_pic in rt['piclist']:
                if one_pic['isvideo'] == 1:
                    media_type = 'pic_video'
                else:
                    media_type = 'pic'
                try:
                    insert_sql = 'INSERT IGNORE INTO media(type,url,thumb) VALUES (%s,%s,%s);'
                    cursor.execute(insert_sql, (media_type, one_pic['url'], one_pic['thumb']))
                    conn.commit()
                    cursor.execute('SELECT id FROM media WHERE url = %s;', one_pic['url'])
                    rt_pic_id_dict = cursor.fetchone()
                    rt_pic_id_list.append(rt_pic_id_dict['id'])
                    logger.info('Successfully insert picture information into database')
                except Exception:
                    logger.error('Error when trying to insert picture information into database')
            rt_pic_id_list = str(rt_pic_id_list)
        else:
            rt_pic_id_list = None
        if rt['video'] is not None:
            rt_video_id_list = []
            try:
                insert_sql = 'INSERT IGNORE INTO media(type, url, thumb) VALUES (%s, %s, %s);'
                cursor.execute(insert_sql, ('video', rt['video']['url'], rt['video']['thumb']))
                conn.commit()
                cursor.execute('SELECT id FROM media WHERE url = %s;', (rt['video']['url']))
                rt_video_id_dict = cursor.fetchone()
                rt_video_id_list.append(rt_video_id_dict['id'])
                logger.info('Successfully insert video information into database')
            except Exception:
                logger.error('Error when trying to insert video information into database')
            rt_video_id_list = str(rt_video_id_list)
        else:
            rt_video_id_list = None
        if cursor.execute('SELECT * FROM rt WHERE tid = %s;', (rt['tid'])) == 0:
            try:
                insert_sql = '''INSERT INTO rt(tid, qq, content, picnum, piclist,
                                               video, device, location_user, location_real, longitude,
                                               latitude, photo_time)
                                    VALUES (%s, %s, %s, %s, %s,
                                            %s, %s, %s, %s, %s,
                                            %s, FROM_UNIXTIME(%s));'''
                cursor.execute(insert_sql, (
                    rt['tid'], rt['qq'], rt['content'], rt['picnum'], rt_pic_id_list,
                    rt_video_id_list, rt['device'], rt['location_user'], rt['location_real'], rt['longitude'],
                    rt['latitude'], rt['photo_time']))
                conn.commit()
                logger.info('Successfully insert rt data into database')
            except Exception:
                logger.error('Error when trying to insert rt data into database')
        else:
            try:
                update_sql = '''UPDATE rt
                                  SET qq = %s, content = %s, picnum = %s, piclist = %s, video = %s,
                                      device = %s, location_user = %s, location_real = %s, longitude = %s,
                                      latitude = %s, photo_time = FROM_UNIXTIME(%s)
                                  WHERE tid = %s;'''
                cursor.execute(update_sql, (rt['qq'], rt['content'], rt['picnum'], rt_pic_id_list, rt_video_id_list,
                                            rt['device'], rt['location_user'], rt['location_real'], rt['longitude'],
                                            rt['latitude'], rt['photo_time'],
                                            rt['tid']))
                conn.commit()
                logger.info('Successfully update rt data into database')
            except Exception:
                logger.error('Error when trying to update rt data into database')
    else:
        rt_tid = None
    if parse['piclist'] is not None:
        pic_id_list = []
        for one_pic in parse['piclist']:
            if one_pic['isvideo'] == 1:
                media_type = 'pic_video'
            else:
                media_type = 'pic'
            try:
                insert_sql = 'INSERT IGNORE INTO media(type, url, thumb) VALUES (%s, %s, %s);'
                cursor.execute(insert_sql, (media_type, one_pic['url'], one_pic['thumb']))
                conn.commit()
                cursor.execute('SELECT id FROM media WHERE url = %s;', one_pic['url'])
                pic_id_dict = cursor.fetchone()
                pic_id_list.append(pic_id_dict['id'])
                logger.info('Successfully insert picture information into database')
            except Exception:
                logger.error('Error when trying to insert picture information into database')
        pic_id_list = str(pic_id_list)
    else:
        pic_id_list = None
    if parse['video'] is not None:
        video_id_list = []
        try:
            insert_sql = 'INSERT IGNORE INTO media(type, url, thumb) VALUES (%s, %s, %s);'
            cursor.execute(insert_sql, ('video', parse['video']['url'], parse['video']['thumb']))
            conn.commit()
            cursor.execute('SELECT id FROM media WHERE url = %s;', (parse['video']['url']))
            video_id_dict = cursor.fetchone()
            video_id_list.append(video_id_dict['id'])
            logger.info('Successfully insert video information into database')
        except Exception:
            logger.error('Error when trying to insert video information into database')
        video_id_list = str(video_id_list)
    else:
        video_id_list = None
    if parse['voice'] is not None:
        voice_id_list = []
        try:
            insert_sql = 'INSERT IGNORE INTO media(type,url,time) VALUES (%s,%s,%s);'
            cursor.execute(insert_sql, ('voice', parse['voice']['url'], parse['voice']['time']*1000))
            conn.commit()
            cursor.execute('SELECT id FROM media WHERE url = %s;', parse['voice']['url'])
            voice_id_dict = cursor.fetchone()
            voice_id_list.append(voice_id_dict['id'])
            logger.info('Successfully insert audio information into database')
        except Exception:
            logger.error('Error when trying to insert audio information into database')
        voice_id_list = str(voice_id_list)
    else:
        voice_id_list = None

    try:
        insert_sql = '''INSERT IGNORE INTO message(catch_time, tid, qq, post_time, rt_tid,
                                                   content, picnum, piclist, video, voice,
                                                   device, location_user, location_real, longitude, latitude,
                                                   photo_time, commentnum)
                            VALUES (FROM_UNIXTIME(%s), %s, %s, FROM_UNIXTIME(%s), %s,
                                    %s, %s, %s, %s, %s,
                                    %s, %s, %s, %s, %s,
                                    FROM_UNIXTIME(%s), %s);'''
        cursor.execute(insert_sql, (
            parse['catch_time'], parse['tid'], parse['qq'], parse['post_time'], rt_tid,
            parse['content'], parse['picnum'], pic_id_list, video_id_list, voice_id_list,
            parse['device'], parse['location_user'], parse['location_real'], parse['longitude'], parse['latitude'],
            parse['photo_time'], parse['commentnum']))
        conn.commit()
        logger.info('Successfully insert data into database')
    except Exception:
        logger.error('Error when trying to insert data into database')
    if parse['comment'] is not None:
        for comment in parse['comment']:
            if cursor.execute('SELECT * FROM qq WHERE uid = %s AND qq = %s;', (uid, comment['qq'])) == 0:
                try:
                    cursor.execute('INSERT INTO qq(uid, qq, name) VALUES (%s, %s, %s);',
                                   (uid, comment['qq'], comment['name']))
                    conn.commit()
                    logger.info('Successfully insert QQ information of %s in uid %s' % (comment['qq'], uid))
                except Exception:
                    logger.error('Error when trying to insert QQ information of %s in uid %s' % (comment['qq'], uid))
            else:
                if cursor.fetchone()['name'] != comment['name']:
                    try:
                        cursor.execute(
                            'UPDATE qq SET name = %s WHERE uid = %s and qq = %s;',
                            (comment['name'], uid, comment['qq']))
                        conn.commit()
                        logger.info('Successfully update QQ information of %s in uid %s' % (comment['qq'], uid))
                    except Exception:
                        logger.error('Error when trying to update QQ information of %s in uid %s'
                                     % (comment['qq'], uid))
            if comment['piclist'] is not None:
                pic_id_list = []
                for one_comment_pic in comment['piclist']:
                    try:
                        insert_sql = 'INSERT IGNORE INTO media(type, url, thumb) VALUES (%s, %s, %s);'
                        cursor.execute(insert_sql,
                                       ('pic', one_comment_pic['url'], one_comment_pic['thumb']))
                        conn.commit()
                        cursor.execute('SELECT id FROM media WHERE url = %s;', one_comment_pic['url'])
                        pic_id_dict = cursor.fetchone()
                        pic_id_list.append(pic_id_dict['id'])
                        logger.info('Successfully insert picture information into database')
                    except Exception:
                        logger.error('Error when trying to insert picture information into database')
                pic_id_list = str(pic_id_list)
            else:
                pic_id_list = None
            try:
                insert_sql = '''INSERT IGNORE INTO comment_reply(catch_time, tid, commentid, replyid, qq,
                                                             post_time, content, picnum, piclist,
                                                             replynum)
                                VALUES (FROM_UNIXTIME(%s), %s, %s, %s, %s,
                                        FROM_UNIXTIME(%s), %s, %s, %s,
                                        %s);'''
                cursor.execute(insert_sql, (parse['catch_time'], parse['tid'], comment['commentid'], 0, comment['qq'],
                                            comment['post_time'], comment['content'], comment['picnum'], pic_id_list,
                                            comment['replynum']))
                conn.commit()
                logger.info('Successfully insert comment data into database')
            except Exception:
                logger.error('Error when trying to insert comment data into database')
            if comment['reply'] is not None:
                for reply in comment['reply']:
                    if cursor.execute('SELECT * FROM qq WHERE uid = %s AND qq = %s;', (uid, reply['qq'])) == 0:
                        try:
                            cursor.execute('INSERT INTO qq(uid, qq, name) VALUES (%s, %s, %s);',
                                           (uid, reply['qq'], reply['name']))
                            conn.commit()
                            logger.info('Successfully insert QQ information of %s in uid %s' % (reply['qq'], uid))
                        except Exception:
                            logger.error('Error when trying to insert QQ information of %s in uid %s' %
                                         (reply['qq'], uid))
                    else:
                        if cursor.fetchone()['name'] != reply['name']:
                            try:
                                cursor.execute('UPDATE qq SET name = %s WHERE uid = %s and qq = %s;',
                                               (reply['name'], uid, reply['qq']))
                                conn.commit()
                                logger.info('Successfully update QQ information of %s in uid %s' % (reply['qq'], uid))
                            except Exception:
                                logger.error('Error when trying to update QQ information of %s in uid %s' %
                                             (reply['qq'], uid))
                    try:
                        insert_sql = '''INSERT IGNORE INTO comment_reply(catch_time, tid, commentid,
                                                                   replyid, qq, reply_target_qq, post_time, content)
                                                        VALUES (FROM_UNIXTIME(%s), %s, %s,
                                                                %s, %s, %s, FROM_UNIXTIME(%s), %s);'''
                        cursor.execute(insert_sql, (parse['catch_time'], parse['tid'], comment['commentid'],
                                                    reply['replyid'], reply['qq'], reply['reply_target_qq'],
                                                    reply['post_time'], reply['content']))
                        conn.commit()
                        logger.info('Successfully insert reply data into database')
                    except Exception:
                        logger.error('Error when trying to insert reply data into database')
    cursor.close()
    conn.close()


def db_write_fine(parse, db_url, db_database, db_username, db_password, db_port=3306, uid=1):
    conn = pymysql.connect(host=db_url, port=db_port, user=db_username, passwd=db_password,
                           db=db_database, charset="utf8mb4", use_unicode=True)
    logger.info('Successfully connect to MySQL database %s at %s:%s'
                % (db_database, db_url, db_port))
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    if cursor.execute('SELECT * FROM qq WHERE uid = %s AND qq = %s;', (uid, parse['qq'])) == 0:
        try:
            cursor.execute('INSERT INTO qq(uid, qq, name) VALUES (%s, %s, %s);', (uid, parse['qq'], parse['name']))
            conn.commit()
            logger.info('Successfully insert QQ information of %s in uid %s' % (parse['qq'], uid))
        except Exception:
            logger.error('Error when trying to insert QQ information of %s in uid %s' % (parse['qq'], uid))
    else:
        if cursor.fetchone()['name'] != parse['name']:
            try:
                cursor.execute('UPDATE qq SET name = %s WHERE uid = %s and qq = %s;', (parse['name'], uid, parse['qq']))
                conn.commit()
                logger.info('Successfully update QQ information of %s in uid %s' % (parse['qq'], uid))
            except Exception:
                logger.error('Error when trying to update QQ information of %s in uid %s' % (parse['qq'], uid))
    if parse['rt'] is not None:
        rt = parse['rt']
        rt_tid = rt['tid']
        if cursor.execute('SELECT * FROM qq WHERE uid = %s AND qq = %s;', (uid, rt['qq'])) == 0:
            try:
                cursor.execute('INSERT INTO qq(uid, qq, name) VALUES (%s, %s, %s);',
                               (uid, rt['qq'], rt['name']))
                conn.commit()
                logger.info('Successfully insert QQ information of %s in uid %s' % (rt['qq'], uid))
            except Exception:
                logger.error('Error when trying to insert QQ information of %s in uid %s' % (rt['qq'], uid))
        else:
            if cursor.fetchone()['name'] != rt['name']:
                try:
                    cursor.execute('UPDATE qq SET name = %s WHERE uid = %s and qq = %s;',
                                   (rt['name'], uid, rt['qq']))
                    conn.commit()
                    logger.info('Successfully update QQ information of %s in uid %s' % (rt['qq'], uid))
                except Exception:
                    logger.error('Error when trying to update QQ information of %s in uid %s'
                                 % (rt['qq'], uid))
        if rt['piclist'] is not None:
            rt_pic_id_list = []
            for one_pic in rt['piclist']:
                if one_pic['isvideo'] == 1:
                    media_type = 'pic_video'
                else:
                    media_type = 'pic'
                try:
                    insert_sql = 'INSERT IGNORE INTO media(type, url, thumb) VALUES (%s, %s, %s);'
                    cursor.execute(insert_sql, (media_type, one_pic['url'], one_pic['thumb']))
                    conn.commit()
                    cursor.execute('SELECT id FROM media WHERE url = %s;', one_pic['url'])
                    rt_pic_id_dict = cursor.fetchone()
                    rt_pic_id_list.append(rt_pic_id_dict['id'])
                    logger.info('Successfully insert picture information into database')
                except Exception:
                    logger.error('Error when trying to insert picture information into database')
            rt_pic_id_list = str(rt_pic_id_list)
        else:
            rt_pic_id_list = None
        if rt['video'] is not None:
            rt_video_id_list = []
            try:
                insert_sql = 'INSERT IGNORE INTO media(type, url, thumb, time) VALUES (%s, %s, %s, %s);'
                cursor.execute(insert_sql, ('video', rt['video']['url'], rt['video']['thumb'], rt['video']['time']))
                conn.commit()
                cursor.execute('SELECT id FROM media WHERE url = %s;', (rt['video']['url']))
                rt_video_id_dict = cursor.fetchone()
                rt_video_id_list.append(rt_video_id_dict['id'])
                logger.info('Successfully insert video information into database')
            except Exception:
                logger.error('Error when trying to insert video information into database')
            rt_video_id_list = str(rt_video_id_list)
        else:
            rt_video_id_list = None
        if cursor.execute('SELECT * FROM rt WHERE tid = %s;', (rt['tid'])) == 0:
            try:
                insert_sql = '''INSERT INTO rt(tid, qq, post_time, content, picnum,
                                               piclist, video, device, location_user,
                                               location_real, longitude, latitude, photo_time)
                                    VALUES (%s, %s, FROM_UNIXTIME(%s), %s, %s,
                                            %s, %s, %s, %s, %s,
                                            %s, %s, FROM_UNIXTIME(%s));'''
                cursor.execute(insert_sql, (rt['tid'], rt['qq'], rt['post_time'], rt['content'], rt['picnum'],
                                            rt_pic_id_list, rt_video_id_list, rt['device'], rt['location_user'],
                                            rt['location_real'], rt['longitude'], rt['latitude'], rt['photo_time']))
                conn.commit()
                logger.info('Successfully insert rt data into database')
            except Exception:
                logger.error('Error when trying to insert rt data into database')
        else:
            try:
                update_sql = '''UPDATE rt
                                  SET qq = %s, post_time = FROM_UNIXTIME(%s), content = %s, picnum = %s, piclist = %s,
                                      video = %s, device = %s, location_user = %s, location_real = %s,
                                      longitude = %s, latitude = %s, photo_time = %s
                                  WHERE tid = %s;'''
                cursor.execute(update_sql, (rt['qq'], rt['post_time'], rt['content'], rt['picnum'], rt_pic_id_list,
                                            rt_video_id_list, rt['device'], rt['location_user'], rt['location_real'],
                                            rt['longitude'], rt['latitude'], rt['photo_time'], rt['tid']))
                conn.commit()
                logger.info('Successfully update rt data into database')
            except Exception:
                logger.error('Error when trying to update rt data into database')
    else:
        rt_tid = None
    if parse['piclist'] is not None:
        pic_id_list = []
        for one_pic in parse['piclist']:
            if one_pic['isvideo'] == 1:
                media_type = 'pic_video'
            else:
                media_type = 'pic'
            try:
                insert_sql = 'INSERT IGNORE INTO media(type, url, thumb) VALUES (%s, %s, %s);'
                cursor.execute(insert_sql, (media_type, one_pic['url'], one_pic['thumb']))
                conn.commit()
                cursor.execute('SELECT id FROM media WHERE url = %s;', one_pic['url'])
                pic_id_dict = cursor.fetchone()
                pic_id_list.append(pic_id_dict['id'])
                logger.info('Successfully insert picture information into database')
            except Exception:
                logger.error('Error when trying to insert picture information into database')
        pic_id_list = str(pic_id_list)
    else:
        pic_id_list = None
    if parse['video'] is not None:
        video_id_list = []
        try:
            insert_sql = 'INSERT IGNORE INTO media(type, url, thumb, time) VALUES (%s, %s, %s, %s);'
            cursor.execute(insert_sql, ('video', parse['video']['url'], parse['video']['thumb'],
                                        parse['video']['time']))
            conn.commit()
            cursor.execute('SELECT id FROM media WHERE url = %s;', parse['video']['url'])
            video_id_dict = cursor.fetchone()
            video_id_list.append(video_id_dict['id'])
            logger.info('Successfully insert vidio information into database')
        except Exception:
            logger.error('Error when trying to insert video information into database')
        video_id_list = str(video_id_list)
    else:
        video_id_list = None
    if parse['voice'] is not None:
        voice_id_list = []
        try:
            insert_sql = 'INSERT IGNORE INTO media(type, url, time) VALUES (%s, %s, %s);'
            cursor.execute(insert_sql, ('voice', parse['voice']['url'], parse['voice']['time']*1000))
            conn.commit()
            cursor.execute('SELECT id FROM media WHERE url = %s;', parse['voice']['url'])
            voice_id_dict = cursor.fetchone()
            voice_id_list.append(voice_id_dict['id'])
            logger.info('Successfully insert audio information into database')
        except Exception:
            logger.error('Error when trying to insert audio information into database')
        voice_id_list = str(voice_id_list)
    else:
        voice_id_list = None
    try:
        insert_sql = '''INSERT IGNORE INTO message(catch_time, tid, qq, post_time, rt_tid,
                                                   content, picnum, piclist, video, voice,
                                                   device, location_user, location_real, longitude, latitude,
                                                   photo_time, viewnum, likenum, forwardnum, commentnum)
                            VALUES (FROM_UNIXTIME(%s), %s, %s, FROM_UNIXTIME(%s), %s,
                                    %s, %s, %s, %s, %s,
                                    %s, %s, %s, %s, %s,
                                    FROM_UNIXTIME(%s), %s, %s, %s, %s);'''
        cursor.execute(insert_sql, (
            parse['catch_time'], parse['tid'], parse['qq'], parse['post_time'], rt_tid,
            parse['content'], parse['picnum'], pic_id_list, video_id_list, voice_id_list,
            parse['device'], parse['location_user'], parse['location_real'], parse['longitude'], parse['latitude'],
            parse['photo_time'], parse['viewnum'], parse['likenum'], parse['forwardnum'], parse['commentnum']))
        conn.commit()
        logger.info('Successfully insert data into database')
    except Exception:
        logger.error('Error when trying to insert data into database')
    if parse['like'] is not None:
        for likeman in parse['like']:
            try:
                cursor.execute('INSERT IGNORE INTO like_person(tid, commentid, qq) VALUES (%s, %s, %s);',
                               (parse['tid'], 0, likeman['qq']))
                conn.commit()
                logger.info('Successfully insert like information of tid %s' % parse['tid'])
            except Exception:
                logger.info('Error when trying to insert like information of tid %s' % parse['tid'])
            if cursor.execute('SELECT * FROM qq WHERE uid = %s AND qq = %s;', (uid, likeman['qq'])) == 0:
                try:
                    cursor.execute('INSERT INTO qq(uid, qq, name) VALUES (%s, %s, %s);',
                                   (uid, likeman['qq'], likeman['name']))
                    conn.commit()
                    logger.info('Successfully insert QQ information of %s in uid %s' % (likeman['qq'], uid))
                except Exception:
                    logger.error('Error when trying to insert QQ information of %s in uid %s' %
                                 (likeman['qq'], uid))
            else:
                if cursor.fetchone()['name'] != likeman['name']:
                    try:
                        cursor.execute('UPDATE qq SET name = %s WHERE uid = %s and qq = %s;',
                                       (likeman['name'], uid, likeman['qq']))
                        conn.commit()
                        logger.info('Successfully update QQ information of %s in uid %s' % (likeman['qq'], uid))
                    except Exception:
                        logger.error('Error when trying to update QQ information of %s in uid %s' %
                                     (likeman['qq'], uid))
    if parse['forward'] is not None:
        for forwardman in parse['forward']:
            try:
                cursor.execute('INSERT IGNORE INTO forward(tid, qq) VALUES (%s, %s);',
                               (parse['tid'], forwardman['qq']))
                conn.commit()
                logger.info('Successfully insert forward information of tid %s' % parse['tid'])
            except Exception:
                logger.info('Error when trying to insert forward information of tid %s' % parse['tid'])
            if cursor.execute('SELECT * FROM qq WHERE uid = %s AND qq = %s;', (uid, forwardman['qq'])) == 0:
                try:
                    cursor.execute('INSERT INTO qq(uid, qq, name) VALUES (%s, %s, %s);',
                                   (uid, forwardman['qq'], forwardman['name']))
                    conn.commit()
                    logger.info('Successfully insert QQ information of %s in uid %s' % (forwardman['qq'], uid))
                except Exception:
                    logger.error('Error when trying to insert QQ information of %s in uid %s' %
                                 (forwardman['qq'], uid))
            else:
                if cursor.fetchone()['name'] != forwardman['name']:
                    try:
                        cursor.execute('UPDATE qq SET name = %s WHERE uid = %s and qq = %s;',
                                       (forwardman['name'], uid, forwardman['qq']))
                        conn.commit()
                        logger.info('Successfully update QQ information of %s in uid %s' % (forwardman['qq'], uid))
                    except Exception:
                        logger.error('Error when trying to update QQ information of %s in uid %s' %
                                     (forwardman['qq'], uid))
    if parse['comment'] is not None:
        for comment in parse['comment']:
            if cursor.execute('SELECT * FROM qq WHERE uid = %s AND qq = %s;', (uid, comment['qq'])) == 0:
                try:
                    cursor.execute('INSERT INTO qq(uid, qq, name) VALUES (%s, %s, %s);',
                                   (uid, comment['qq'], comment['name']))
                    conn.commit()
                    logger.info('Successfully insert QQ information of %s in uid %s' % (comment['qq'], uid))
                except Exception:
                    logger.error('Error when trying to insert QQ information of %s in uid %s' % (comment['qq'], uid))
            else:
                if cursor.fetchone()['name'] != comment['name']:
                    try:
                        cursor.execute('UPDATE qq SET name = %s WHERE uid = %s and qq = %s;',
                                       (comment['name'], uid, comment['qq']))
                        conn.commit()
                        logger.info('Successfully update QQ information of %s in uid %s' % (comment['qq'], uid))
                    except Exception:
                        logger.error('Error when trying to update QQ information of %s in uid %s'
                                     % (comment['qq'], uid))
            if comment['piclist'] is not None:
                pic_id_list = []
                for one_comment_pic in comment['piclist']:
                    try:
                        insert_sql = 'INSERT IGNORE INTO media(type, url, thumb) VALUES (%s, %s, %s);'
                        cursor.execute(insert_sql,
                                       ('pic', one_comment_pic['url'], one_comment_pic['thumb']))
                        conn.commit()
                        cursor.execute('SELECT id FROM media WHERE url=%s;', one_comment_pic['url'])
                        pic_id_dict = cursor.fetchone()
                        pic_id_list.append(pic_id_dict['id'])
                        logger.info('Successfully insert picture information into database')
                    except Exception:
                        logger.error('Error when trying to insert picture information into database')
                pic_id_list = str(pic_id_list)
            else:
                pic_id_list = None
            try:
                insert_sql = '''INSERT IGNORE INTO comment_reply(catch_time, tid, commentid, replyid, qq,
                                                             post_time, content, picnum, piclist,
                                                             likenum, replynum)
                                VALUES (FROM_UNIXTIME(%s), %s, %s, %s, %s,
                                        FROM_UNIXTIME(%s), %s, %s, %s,
                                        %s, %s);'''
                cursor.execute(insert_sql, (parse['catch_time'], parse['tid'], comment['commentid'], 0, comment['qq'],
                                            comment['post_time'], comment['content'], comment['picnum'], pic_id_list,
                                            comment['likenum'], comment['replynum']))
                conn.commit()
                logger.info('Successfully insert comment data into database')
            except Exception:
                logger.error('Error when trying to insert comment data into database')
            if comment['like'] is not None:
                for likeman in comment['like']:
                    try:
                        cursor.execute('INSERT IGNORE INTO like_person(tid, commentid, qq) VALUES (%s, %s, %s);',
                                       (parse['tid'], comment['commentid'], likeman['qq']))
                        conn.commit()
                        logger.info('Successfully insert like information of comment %s in tid %s'
                                    % (comment['commentid'], parse['tid']))
                    except Exception:
                        logger.info('Error when trying to insert like information of comment %s in tid %s'
                                    % (comment['commentid'], parse['tid']))
                    if cursor.execute('SELECT * FROM qq WHERE uid = %s AND qq = %s;', (uid, likeman['qq'])) == 0:
                        try:
                            cursor.execute('INSERT INTO qq(uid, qq, name) VALUES (%s, %s, %s);',
                                           (uid, likeman['qq'], likeman['name']))
                            conn.commit()
                            logger.info('Successfully insert QQ information of %s in uid %s' % (likeman['qq'], uid))
                        except Exception:
                            logger.error('Error when trying to insert QQ information of %s in uid %s' %
                                         (likeman['qq'], uid))
                    else:
                        if cursor.fetchone()['name'] != likeman['name']:
                            try:
                                cursor.execute('UPDATE qq SET name = %s WHERE uid = %s and qq = %s;',
                                               (likeman['name'], uid, likeman['qq']))
                                conn.commit()
                                logger.info('Successfully update QQ information of %s in uid %s' % (likeman['qq'], uid))
                            except Exception:
                                logger.error('Error when trying to update QQ information of %s in uid %s' %
                                             (likeman['qq'], uid))
            if comment['reply'] is not None:
                for reply in comment['reply']:
                    if cursor.execute('SELECT * FROM qq WHERE uid = %s AND qq = %s;', (uid, reply['qq'])) == 0:
                        try:
                            cursor.execute('INSERT INTO qq(uid, qq, name) VALUES (%s, %s, %s);',
                                           (uid, reply['qq'], reply['name']))
                            conn.commit()
                            logger.info('Successfully insert QQ information of %s in uid %s' % (reply['qq'], uid))
                        except Exception:
                            logger.error('Error when trying to insert QQ information of %s in uid %s' %
                                         (reply['qq'], uid))
                    else:
                        if cursor.fetchone()['name'] != reply['name']:
                            try:
                                cursor.execute('UPDATE qq SET name = %s WHERE uid = %s and qq = %s;',
                                               (reply['name'], uid, reply['qq']))
                                conn.commit()
                                logger.info('Successfully update QQ information of %s in uid %s' % (reply['qq'], uid))
                            except Exception:
                                logger.error('Error when trying to update QQ information of %s in uid %s' %
                                             (reply['qq'], uid))
                    try:
                        insert_sql = '''INSERT IGNORE INTO comment_reply(catch_time, tid, commentid,
                                                                   replyid, qq, reply_target_qq, post_time, content)
                                                        VALUES (FROM_UNIXTIME(%s), %s, %s,
                                                                %s, %s, %s, FROM_UNIXTIME(%s), %s);'''
                        cursor.execute(insert_sql, (parse['catch_time'], parse['tid'], comment['commentid'],
                                                    reply['replyid'], reply['qq'], reply['reply_target_qq'],
                                                    reply['post_time'], reply['content']))
                        conn.commit()
                        logger.info('Successfully insert reply data into database')
                    except Exception:
                        logger.error('Error when trying to insert reply data into database')
    cursor.close()
    conn.close()
