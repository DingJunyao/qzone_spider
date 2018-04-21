#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" MySQL connection and insert of qzone_spider """

__author__ = 'Ding Junyao'

import sqlite3
import logging
from qzone_spider import svar

logger = logging.getLogger(__name__)

create_table_sql = (
    '''CREATE TABLE "message" (
  "catch_time" INTEGER NOT NULL,
  "tid" TEXT NOT NULL,
  "qq"  INTEGER NOT NULL,
  "post_time"  INTEGER NOT NULL,
  "rt_tid"  TEXT DEFAULT NULL,
  "content" TEXT  DEFAULT NULL,
  "picnum"  INTEGER  DEFAULT NULL,
  "videonum"  INTEGER DEFAULT NULL,
  "sharelink" TEXT  DEFAULT NULL,
  "piclist" TEXT  DEFAULT NULL,
  "video" TEXT  DEFAULT NULL,
  "voice" TEXT  DEFAULT NULL,
  "device"  TEXT  DEFAULT NULL,
  "location_user"  TEXT  DEFAULT NULL,
  "location_real"  TEXT  DEFAULT NULL,
  "longitude" REAL  DEFAULT NULL,
  "latitude" REAL  DEFAULT NULL,
  "altitude" REAL  DEFAULT NULL,
  "photo_time"  INTEGER DEFAULT NULL,
  "viewnum" INTEGER DEFAULT NULL,
  "likenum" INTEGER DEFAULT NULL,
  "forwardnum" INTEGER DEFAULT NULL,
  "commentnum" INTEGER DEFAULT NULL,
  PRIMARY KEY ("catch_time","tid")
);''',
    '''CREATE TABLE "rt" (
  "tid" TEXT NOT NULL,
  "qq"  INTEGER NOT NULL,
  "post_time"  INTEGER NOT NULL,
  "content" TEXT DEFAULT NULL,
  "picnum"  INTEGER  DEFAULT NULL,
  "videonum"  INTEGER DEFAULT NULL,
  "pic" TEXT  DEFAULT NULL,
  "video" TEXT  DEFAULT NULL,
  "device"  TEXT  DEFAULT NULL,
  "forwardnum" INTEGER DEFAULT NULL,
  PRIMARY KEY ("tid")
);''',
    '''CREATE TABLE "like_thumb"(
  "tid" TEXT NOT NULL,
  "commentid" INTEGER DEFAULT NULL,
  "qq"  INTEGER NOT NULL,
  PRIMARY KEY ("tid","commentid","qq")
);''',
    '''CREATE TABLE "comment"(
  "catch_time" INTEGER NOT NULL,
  "tid" TEXT NOT NULL,
  "commentid" INTEGER NOT NULL,
  "replyid" INTEGER NOT NULL,
  "qq"  INTEGER NOT NULL,
  "reply_target_qq"  INTEGER DEFAULT NULL,
  "post_time"  INTEGER NOT NULL,
  "content" TEXT  DEFAULT NULL,
  "picnum"  INTEGER  DEFAULT NULL,
  "pic" TEXT  DEFAULT NULL,
  "likenum" INTEGER DEFAULT NULL,
  "replynum" INTEGER DEFAULT NULL,
  PRIMARY KEY ("catch_time","tid","commentid","replyid")
);''',
    '''CREATE TABLE "media"(
  "id"  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  "type"  TEXT  NOT NULL,
  "url" TEXT  NOT NULL UNIQUE,
  "thumb" TEXT  DEFAULT NULL,
  "time" INTEGER  DEFAULT NULL
);''',
    '''CREATE TABLE "qq"(
  "qq"  INTEGER  NOT NULL,
  "name" TEXT DEFAULT NULL,
  "memo"  TEXT	DEFAULT NULL,
  PRIMARY KEY ("qq")
);''',
    '''CREATE TABLE "message_memo" (
  "id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  "tid" TEXT NOT NULL,
  "memo"  TEXT	NOT NULL
);''',
    '''CREATE TABLE "comment_memo"(
  "id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  "tid" TEXT NOT NULL,
  "commentid" INTEGER NOT NULL,
  "replyid" INTEGER NOT NULL,
  "memo"  TEXT	NOT NULL
);''',
    '''CREATE TABLE "media_memo" (
  "id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  "media_id" INTEGER NOT NULL,
  "memo"  TEXT	NOT NULL
);''')
# TODO: The SQL is not finished.


def db_init():
    conn = sqlite3.connect(svar.dbURL)
    # logger.info('成功连接至%s数据库 %s' % % (svar.dbType, svar.dbURL))
    logger.info('Successfully connect to %s database %s' % (svar.dbType, svar.dbURL))
    cursor = conn.cursor()
    for i in create_table_sql:
        cursor.execute(i)
    # logger.info('数据库初始化完成')
    logger.info('Database initialized')
    cursor.close()
    conn.close()


def db_write_rough(parse):
    conn = sqlite3.connect(svar.dbURL)
    # logger.info('成功连接至%s数据库 %s' % % (svar.dbType, svar.dbURL))
    logger.info('Successfully connect to %s database %s' % (svar.dbType, svar.dbURL))
    cursor = conn.cursor()
    if parse['voice'] is not None:
        voice_id_list = []
        try:
            insert_sql = 'INSERT OR IGNORE INTO media(type,url,time) VALUES (%s,%s,%s);'
            cursor.execute(insert_sql, ('voice', parse['voice']['url'], parse['voice']['time']*1000))
            conn.commit()
            cursor.execute('SELECT id FROM media WHERE url=%s;', (parse['voice']['url'],))
            voiceidtuple = cursor.fetchall()
            voice_id_list.append(voiceidtuple[0][0])
            # logger.info('成功将音频信息插入到数据库')
            logger.info('Successfully insert audio information into database')
        except Exception:
            # logger.error('试图将音频信息存入数据库时出错')
            logger.error('Error when trying to insert audio information into database')
        voice_id_list = str(voice_id_list)
    else:
        voice_id_list = None
    try:
        insert_sql = '''INSERT OR IGNORE INTO message(catch_time, tid, qq, post_time, rt_tid, 
                                                      content, picnum, videonum, sharelink, voice, 
                                                      device, location_user, location_real, longitude, latitude, 
                                                      photo_time, commentnum)
                            VALUES (?, ?, ?, ?, ?, 
                                    ?, ?, ?, ?, ?, 
                                    ?, ?, ?, ?, ?, 
                                    ?, ?);'''
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
    conn = sqlite3.connect(svar.dbURL)
    # logger.info('成功连接至%s数据库 %s' % % (svar.dbType, svar.dbURL))
    logger.info('Successfully connect to %s database %s' % (svar.dbType, svar.dbURL))
    cursor = conn.cursor()
    if parse['piclist'] is not None:
        pic_id_list = []
        for i in range(len(parse['piclist'])):
            if parse['piclist'][i]['isvideo'] == 1:
                media_type = 'pic_video'
            else:
                media_type = 'pic'
            try:
                insert_sql = 'INSERT OR IGNORE INTO media(type,url,thumb) VALUES (?,?,?);'
                cursor.execute(insert_sql, (media_type, parse['piclist'][i]['url'], parse['piclist'][i]['thumb']))
                conn.commit()
                cursor.execute('SELECT id FROM media WHERE url=?;', (parse['piclist'][i]['url'],))
                picidtuple = cursor.fetchall()
                pic_id_list.append(picidtuple[0][0])
                # logger.info('成功将图片信息插入到数据库')
                logger.info('Successfully insert picture information into database')
            except Exception as e:
                # logger.error('试图将图片信息存入数据库时出错')
                logger.error('Error when trying to insert picture information into database')
        pic_id_list = str(pic_id_list)
    else:
        pic_id_list = None
    if parse['voice'] is not None:
        voice_id_list = []
        try:
            insert_sql = 'INSERT OR IGNORE INTO media(type,url,time) VALUES (?,?,?);'
            cursor.execute(insert_sql, ('voice', parse['voice']['url'], parse['voice']['time']*1000))
            conn.commit()
            cursor.execute('SELECT id FROM media WHERE url=?;', (parse['voice']['url'],))
            voiceidtuple = cursor.fetchall()
            voice_id_list.append(voiceidtuple[0][0])
            # logger.info('成功将音频信息插入到数据库')
            logger.info('Successfully insert audio information into database')
        except Exception as e:
            # logger.error('试图将音频信息存入数据库时出错')
            logger.error('Error when trying to insert audio information into database')
        voice_id_list = str(voice_id_list)
    else:
        voice_id_list = None
    if parse['video'] is not None:
        video_id_list = []
        try:
            insert_sql = 'INSERT OR IGNORE INTO media(type,url,thumb,time) VALUES (?,?,?,?);'
            cursor.execute(insert_sql, ('video', parse['video']['url'], parse['video']['thumb'],
                                        parse['video']['time']))
            conn.commit()
            cursor.execute('SELECT id FROM media WHERE url=?;', (parse['video']['url'],))
            videoidtuple = cursor.fetchall()
            video_id_list.append(videoidtuple[0][0])

            # logger.info('成功将视频信息插入到数据库')
            logger.info('Successfully insert video information into database')
        except Exception as e:
            # logger.error('试图将视频信息存入数据库时出错')
            logger.error('Error when trying to insert video information into database')
        video_id_list = str(video_id_list)
    else:
        video_id_list = None
    try:
        insert_sql = '''INSERT OR IGNORE INTO message(catch_time, tid, qq, post_time, rt_tid, 
                                                      content, picnum, videonum, sharelink, piclist, 
                                                      video, voice, device, location_user, location_real, 
                                                      longitude, latitude, altitude, photo_time, viewnum, 
                                                      likenum, forwardnum, commentnum)
                            VALUES (?, ?, ?, ?, ?, 
                                    ?, ?, ?, ?, ?, 
                                    ?, ?, ?, ?, ?, 
                                    ?, ?, ?, ?, ?, 
                                    ?, ?, ?);'''
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
    except Exception as e:
        # logger.error('试图将数据插入到数据库中出错')
        logger.error('Error when trying to insert data into database')
    finally:
        cursor.close()
        conn.close()
