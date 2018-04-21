#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" MySQL connection and insert of qzone_spider """

__author__ = 'Ding Junyao'

import pymysql
from qzone_spider import svar
import logging

logger = logging.getLogger(__name__)

create_table_sql = (
    '''CREATE TABLE `user` (
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
        `videonum`  INT(3) DEFAULT NULL,
        `sharelink` TEXT  DEFAULT NULL,
        `piclist` TEXT  DEFAULT NULL,
        `video` TEXT  DEFAULT NULL,
        `voice` TEXT  DEFAULT NULL,
        `device`  VARCHAR(100)  DEFAULT NULL,
        `location_user`  VARCHAR(100)  DEFAULT NULL,
        `location_real`  VARCHAR(100)  DEFAULT NULL,
        `longitude` DOUBLE(11,7)  DEFAULT NULL,
        `latitude` DOUBLE(11,7)  DEFAULT NULL,
        `altitude` DOUBLE(11,7)  DEFAULT NULL,
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
        `post_time`  DATETIME NOT NULL,
        `content` TEXT DEFAULT NULL,
        `picnum`  INT(3)  DEFAULT NULL,
        `videonum`  INT(3) DEFAULT NULL,
        `pic` TEXT  DEFAULT NULL,
        `video` TEXT  DEFAULT NULL,
        `device`  VARCHAR(100)  DEFAULT NULL,
        `forwardnum` INT(11) DEFAULT NULL,
        PRIMARY KEY (`tid`)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;''',
    '''CREATE TABLE `like_thumb`(
        `tid` VARCHAR(26) NOT NULL,
        `commentid` INT(11) DEFAULT NULL,
        `qq`  BIGINT(16) NOT NULL,
        PRIMARY KEY (`tid`,`commentid`,`qq`)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;''',
    '''CREATE TABLE `comment`(
        `catch_time` DATETIME NOT NULL,
        `tid` VARCHAR(26) NOT NULL,
        `commentid` INT(11) NOT NULL,
        `replyid` INT(11) NOT NULL,
        `qq`  BIGINT(16) NOT NULL,
        `reply_target_qq`  BIGINT(16) DEFAULT NULL,
        `post_time`  DATETIME NOT NULL,
        `content` TEXT  DEFAULT NULL,
        `picnum`  INT(2)  DEFAULT NULL,
        `pic` TEXT  DEFAULT NULL,
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
    '''CREATE TABLE `comment_memo`(
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
# TODO: The SQL is not finished.


def db_init():
    conn = pymysql.connect(host=svar.dbURL, port=svar.dbPort, user=svar.dbUsername, passwd=svar.dbPassword,
                           db=svar.dbDatabase, charset="utf8mb4", use_unicode=True)
    # logger.info('成功连接至在 %s:%s 的 %s 数据库 %s' % (svar.dbURL, svar.dbPort, svar.dbType, svar.dbDatabase))
    logger.info('Successfully connect to %s database %s at %s:%s'
                % (svar.dbType, svar.dbDatabase, svar.dbURL, svar.dbPort))
    cursor = conn.cursor()
    for i in create_table_sql:
        cursor.execute(i)
    # logger.info('数据库初始化完成')
    logger.info('Database initialized')
    cursor.close()
    conn.close()


def db_write_rough(parse):
    conn = pymysql.connect(host=svar.dbURL, port=svar.dbPort, user=svar.dbUsername, passwd=svar.dbPassword,
                           db=svar.dbDatabase, charset="utf8mb4", use_unicode=True)
    # logger.info('成功连接至在 %s:%s 的 %s 数据库 %s' % (svar.dbURL, svar.dbPort, svar.dbType, svar.dbDatabase))
    logger.info('Successfully connect to %s database %s at %s:%s'
                % (svar.dbType, svar.dbDatabase, svar.dbURL, svar.dbPort))
    cursor = conn.cursor()
    if parse['voice'] is not None:
        voice_id_list = []
        try:
            insert_sql = 'INSERT IGNORE INTO media(type,url,time) VALUES (%s,%s,%s);'
            cursor.execute(insert_sql, ('voice', parse['voice']['url'], parse['voice']['time']*1000))
            conn.commit()
            cursor.execute('SELECT id FROM media WHERE url=%s;', parse['voice']['url'])
            voiceidtuple = cursor.fetchall()
            voice_id_list.append(voiceidtuple[0][0])
            # logger.info('成功将音频信息插入到数据库')
            logger.info('Successfully insert audio information into database')
        except Exception:
            # logger.error('试图将音频信息存入数据库时出错')
            logger.error('Error when trying to insert audio information into database')
            pass
        voice_id_list = str(voice_id_list)
    else:
        voice_id_list = None
    try:
        insert_sql = '''INSERT IGNORE INTO message(catch_time, tid, qq, post_time, rt_tid, 
                                                   content, picnum, videonum, sharelink, voice, 
                                                   device, location_user, location_real, longitude, latitude, 
                                                   photo_time, commentnum)
                            VALUES (FROM_UNIXTIME(%s), %s, %s, FROM_UNIXTIME(%s), %s, 
                                    %s, %s, %s, %s, %s, 
                                    %s, %s, %s, %s, %s, 
                                    FROM_UNIXTIME(%s), %s);'''
        cursor.execute(insert_sql, (
            parse['catch_time'], parse['tid'], parse['qq'], parse['post_time'], parse['rt_tid'],
            parse['content'], parse['picnum'], parse['videonum'], parse['sharelink'], voice_id_list,
            parse['device'], parse['location_user'], parse['location_real'], parse['longitude'], parse['latitude'],
            parse['photo_time'], parse['commentnum']
        ))
        conn.commit()
        # logger.info('成功将数据插入到数据库')
        logger.info('Successfully insert data into database')
    except Exception:
        # logger.error('试图将数据插入到数据库中出错')
        logger.error('Error when trying to insert data into database')
    finally:
        cursor.close()
        conn.close()


def db_write_fine(parse):
    conn = pymysql.connect(host=svar.dbURL, port=svar.dbPort, user=svar.dbUsername, passwd=svar.dbPassword,
                           db=svar.dbDatabase, charset="utf8mb4", use_unicode=True)
    # logger.info('成功连接至在 %s:%s 的 %s 数据库 %s' % (svar.dbURL, svar.dbPort, svar.dbType, svar.dbDatabase))
    logger.info('Successfully connect to %s database %s at %s:%s'
                % (svar.dbType, svar.dbDatabase, svar.dbURL, svar.dbPort))
    cursor = conn.cursor()
    if parse['piclist'] is not None:
        pic_id_list = []
        for i in range(len(parse['piclist'])):
            if parse['piclist'][i]['isvideo'] == 1:
                media_type = 'pic_video'
            else:
                media_type = 'pic'
            try:
                insert_sql = 'INSERT IGNORE INTO media(type,url,thumb) VALUES (%s,%s,%s);'
                cursor.execute(insert_sql, (media_type, parse['piclist'][i]['url'], parse['piclist'][i]['thumb']))
                conn.commit()
                cursor.execute('SELECT id FROM media WHERE url=%s;', parse['piclist'][i]['url'])
                picidtuple = cursor.fetchall()
                pic_id_list.append(picidtuple[0][0])
                # logger.info('成功将图片信息插入到数据库')
                logger.info('Successfully insert picture information into database')
            except Exception:
                # logger.error('试图将图片信息存入数据库时出错')
                logger.error('Error when trying to insert picture information into database')
                pass
        pic_id_list = str(pic_id_list)
    else:
        pic_id_list = None
    if parse['voice'] is not None:
        voice_id_list = []
        try:
            insert_sql = 'INSERT IGNORE INTO media(type,url,time) VALUES (%s,%s,%s);'
            cursor.execute(insert_sql, ('voice', parse['voice']['url'], parse['voice']['time']*1000))
            conn.commit()
            cursor.execute('SELECT id FROM media WHERE url=%s;', parse['voice']['url'])
            voiceidtuple = cursor.fetchall()
            voice_id_list.append(voiceidtuple[0][0])
            # logger.info('成功将音频信息插入到数据库')
            logger.info('Successfully insert audio information into database')
        except Exception:
            # logger.error('试图将音频信息存入数据库时出错')
            logger.error('Error when trying to insert audio information into database')
            pass
        voice_id_list = str(voice_id_list)
    else:
        voice_id_list = None
    if parse['video'] is not None:
        video_id_list = []
        try:
            insert_sql = 'INSERT IGNORE INTO media(type,url,thumb,time) VALUES (%s,%s,%s,%s);'
            cursor.execute(insert_sql, ('video', parse['video']['url'], parse['video']['thumb'],
                                        parse['video']['time']))
            conn.commit()
            cursor.execute('SELECT id FROM media WHERE url=%s;', parse['video']['url'])
            videoidtuple = cursor.fetchall()
            video_id_list.append(videoidtuple[0][0])

            # logger.info('成功将视频信息插入到数据库')
            logger.info('Successfully insert vidio information into database')
        except Exception:
            # logger.error('试图将视频信息存入数据库时出错')
            logger.error('Error when trying to insert video information into database')
        video_id_list = str(video_id_list)
    else:
        video_id_list = None
    try:
        insert_sql = '''INSERT IGNORE INTO message(catch_time, tid, qq, post_time, rt_tid, 
                                                   content, picnum, videonum, sharelink, piclist, 
                                                   video, voice, device, location_user, location_real, 
                                                   longitude, latitude, altitude, photo_time, viewnum, 
                                                   likenum, forwardnum, commentnum)
                            VALUES (FROM_UNIXTIME(%s), %s, %s, FROM_UNIXTIME(%s), %s, 
                                    %s, %s, %s, %s, %s, 
                                    %s, %s, %s, %s, %s, 
                                    %s, %s, %s, FROM_UNIXTIME(%s), %s, 
                                    %s, %s, %s);'''
        cursor.execute(insert_sql, (
            parse['catch_time'], parse['tid'], parse['qq'], parse['post_time'], parse['rt_tid'],
            parse['content'], parse['picnum'], parse['videonum'], parse['sharelink'], pic_id_list,
            video_id_list, voice_id_list, parse['device'], parse['location_user'], parse['location_real'],
            parse['longitude'], parse['latitude'], None, parse['photo_time'], parse['viewnum'],
            parse['likenum'], parse['forwardnum'], parse['commentnum']
        ))
        conn.commit()
        # logger.info('成功将数据插入到数据库')
        logger.info('Successfully insert data into database')
    except Warning:
        # logger.error('试图将数据插入到数据库中出错')
        logger.error('Error when trying to insert data into database')
        raise
    finally:
        cursor.close()
        conn.close()
