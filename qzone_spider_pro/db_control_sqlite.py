#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" SQLite connection and insert of qzone_spider """

__author__ = 'Ding Junyao'

import sqlite3
import logging

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
  "piclist" TEXT  DEFAULT NULL,
  "video" TEXT  DEFAULT NULL,
  "voice" TEXT  DEFAULT NULL,
  "device"  TEXT  DEFAULT NULL,
  "location_user"  TEXT  DEFAULT NULL,
  "location_real"  TEXT  DEFAULT NULL,
  "longitude" REAL  DEFAULT NULL,
  "latitude" REAL  DEFAULT NULL,
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
  "post_time"  INTEGER DEFAULT NULL,
  "content" TEXT DEFAULT NULL,
  "picnum"  INTEGER  DEFAULT NULL,
  "piclist" TEXT  DEFAULT NULL,
  "video" TEXT  DEFAULT NULL,
  "device"  TEXT  DEFAULT NULL,
  "location_user"  TEXT  DEFAULT NULL,
  "location_real"  TEXT  DEFAULT NULL,
  "longitude" REAL  DEFAULT NULL,
  "latitude" REAL  DEFAULT NULL,
  "photo_time"  INTEGER DEFAULT NULL,
  PRIMARY KEY ("tid")
);''',
    '''CREATE TABLE "like_person"(
  "tid" TEXT NOT NULL,
  "commentid" INTEGER DEFAULT NULL,
  "qq"  INTEGER NOT NULL,
  PRIMARY KEY ("tid","commentid","qq")
);''',
    '''CREATE TABLE "forward"(
  "tid" TEXT NOT NULL,
  "qq"  INTEGER NOT NULL,
  PRIMARY KEY ("tid","qq")
);''',
    '''CREATE TABLE "comment_reply"(
  "catch_time" INTEGER NOT NULL,
  "tid" TEXT NOT NULL,
  "commentid" INTEGER NOT NULL,
  "replyid" INTEGER NOT NULL,
  "qq"  INTEGER NOT NULL,
  "reply_target_qq"  INTEGER DEFAULT NULL,
  "post_time"  INTEGER NOT NULL,
  "content" TEXT  DEFAULT NULL,
  "picnum"  INTEGER  DEFAULT NULL,
  "piclist" TEXT  DEFAULT NULL,
  "likenum" INTEGER DEFAULT NULL,
  "replynum" INTEGER DEFAULT NULL,
  PRIMARY KEY ("catch_time","tid","commentid","replyid")
);''',
    '''CREATE TABLE "media"(
  "id"  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  "type"  TEXT  NOT NULL,
  "url" TEXT  NOT NULL UNIQUE,
  "thumb" TEXT  DEFAULT NULL,
  "time" INTEGER  DEFAULT NULL,
  "memo" INTEGER  DEFAULT NULL
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
    '''CREATE TABLE "comment_reply_memo"(
  "id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  "tid" TEXT NOT NULL,
  "commentid" INTEGER NOT NULL,
  "replyid" INTEGER NOT NULL,
  "memo"  TEXT	NOT NULL
);''')


def db_init(db_url):
    conn = sqlite3.connect(db_url)
    logger.info('Successfully connect to SQLite database %s' % db_url)
    cursor = conn.cursor()
    for i in create_table_sql:
        cursor.execute(i)
    logger.info('Database initialized')
    cursor.close()
    conn.close()


def _dict_factory(cursor, row):
    return dict((col[0], row[idx]) for idx, col in enumerate(cursor.description))


# noinspection PyTypeChecker
def db_write_rough(parse, db_url):
    conn = sqlite3.connect(db_url)
    logger.info('Successfully connect to SQLite database %s' % db_url)
    conn.row_factory = _dict_factory
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM qq WHERE qq = ?;', (parse['qq'], ))
    qq_fetch = cursor.fetchone()
    if qq_fetch is None:
        try:
            cursor.execute('INSERT INTO qq(qq, "name") VALUES (?, ?);', (parse['qq'], parse['name']))
            conn.commit()
            logger.info('Successfully insert QQ information of %s' % parse['qq'])
        except Exception:
            logger.error('Error when trying to insert QQ information of %s' % parse['qq'])
    else:
        # noinspection PyTypeChecker
        if qq_fetch['name'] != parse['name']:
            try:
                cursor.execute('UPDATE qq SET "name" = ? WHERE qq = ?;', (parse['name'], parse['qq']))
                conn.commit()
                logger.info('Successfully update QQ information of %s' % parse['qq'])
            except Exception:
                logger.error('Error when trying to update QQ information of %s' % parse['qq'])
    if parse['rt'] is not None:
        rt = parse['rt']
        rt_tid = rt['tid']
        cursor.execute('SELECT * FROM qq WHERE qq = ?;', (rt['qq'], ))
        qq_fetch = cursor.fetchone()
        if qq_fetch is None:
            try:
                cursor.execute('INSERT INTO qq(qq, "name") VALUES (?, ?);', (rt['qq'], rt['name']))
                conn.commit()
                logger.info('Successfully insert QQ information of %s' % rt['qq'])
            except Exception:
                logger.error('Error when trying to insert QQ information of %s' % rt['qq'])
        else:
            if qq_fetch['name'] != rt['name']:
                try:
                    cursor.execute('UPDATE qq SET "name" = ? WHERE qq = ?;', (rt['name'], rt['qq']))
                    conn.commit()
                    logger.info('Successfully update QQ information of %s' % rt['qq'])
                except Exception:
                    logger.error('Error when trying to update QQ information of %s' % rt['qq'])
        if rt['piclist'] is not None:
            rt_pic_id_list = []
            for one_pic in rt['piclist']:
                if one_pic['isvideo'] == 1:
                    media_type = 'pic_video'
                else:
                    media_type = 'pic'
                try:
                    insert_sql = 'INSERT OR IGNORE INTO media("type", url, thumb) VALUES (?, ?, ?) '
                    cursor.execute(insert_sql, (media_type, one_pic['url'], one_pic['thumb']))
                    conn.commit()
                    cursor.execute('SELECT id FROM media WHERE url = ?;', (one_pic['url'], ))
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
                insert_sql = 'INSERT OR IGNORE INTO media("type", url, thumb) VALUES (?, ?, ?);'
                cursor.execute(insert_sql, ('video', rt['video']['url'], rt['video']['thumb']))
                conn.commit()
                cursor.execute('SELECT id FROM media WHERE url = ?;', (rt['video']['url'], ))
                rt_video_id_dict = cursor.fetchone()
                rt_video_id_list.append(rt_video_id_dict['id'])
                logger.info('Successfully insert video information into database')
            except Exception:
                logger.error('Error when trying to insert video information into database')
            rt_video_id_list = str(rt_video_id_list)
        else:
            rt_video_id_list = None
        cursor.execute('SELECT * FROM rt WHERE tid = ?;', (rt['tid'], ))
        rt_fetch = cursor.fetchone()
        if rt_fetch is None:
            try:
                insert_sql = '''INSERT INTO rt(tid, qq, "content", picnum, piclist,
                                               video, device, location_user, location_real, longitude,
                                               latitude, photo_time)
                                    VALUES (?, ?, ?, ?, ?,
                                            ?, ?, ?, ?, ?,
                                            ?, ?);'''
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
                                  SET qq = ?, "content" = ?, picnum = ?, piclist = ?, video = ?,
                                      device = ?, location_user = ?, location_real = ?, longitude = ?,
                                      latitude = ?, photo_time = ?
                                  WHERE tid = ?;'''
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
                insert_sql = 'INSERT OR IGNORE INTO media("type", url, thumb) VALUES (?, ?, ?);'
                cursor.execute(insert_sql, (media_type, one_pic['url'], one_pic['thumb']))
                conn.commit()
                cursor.execute('SELECT id FROM media WHERE url = ?;', (one_pic['url'], ))
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
            insert_sql = 'INSERT OR IGNORE INTO media("type", url) VALUES (?, ?);'
            cursor.execute(insert_sql, ('video', parse['video']['url']))
            conn.commit()
            cursor.execute('SELECT id FROM media WHERE url = ?;', (parse['video']['url'], ))
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
            insert_sql = 'INSERT OR IGNORE INTO media(type, url, time) VALUES (?, ?, ?);'
            cursor.execute(insert_sql, ('voice', parse['voice']['url'], parse['voice']['time']*1000))
            conn.commit()
            cursor.execute('SELECT id FROM media WHERE url = ?;', (parse['voice']['url'],))
            voice_id_dict = cursor.fetchone()
            voice_id_list.append(voice_id_dict['id'])
            logger.info('Successfully insert audio information into database')
        except Exception:
            logger.error('Error when trying to insert audio information into database')
        voice_id_list = str(voice_id_list)
    else:
        voice_id_list = None
    try:
        insert_sql = '''INSERT OR IGNORE INTO message(catch_time, tid, qq, post_time, rt_tid,
                                                      content, picnum, piclist, video, voice,
                                                      device, location_user, location_real, longitude, latitude,
                                                      photo_time, commentnum)
                            VALUES (?, ?, ?, ?, ?,
                                    ?, ?, ?, ?, ?,
                                    ?, ?, ?, ?, ?,
                                    ?, ?);'''
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
            cursor.execute('SELECT * FROM qq WHERE qq = ?;', (comment['qq'],))
            qq_fetch = cursor.fetchone()
            if qq_fetch is None:
                try:
                    cursor.execute('INSERT INTO qq(qq, "name") VALUES (?, ?);', (comment['qq'], comment['name']))
                    conn.commit()
                    logger.info('Successfully insert QQ information of %s' % comment['qq'])
                except Exception:
                    logger.error('Error when trying to insert QQ information of %s' % comment['qq'])
            else:
                if qq_fetch['name'] != comment['name']:
                    try:
                        cursor.execute('UPDATE qq SET "name" = ? WHERE qq = ?;', (comment['name'], comment['qq']))
                        conn.commit()
                        logger.info('Successfully update QQ information of %s' % comment['qq'])
                    except Exception:
                        logger.error('Error when trying to update QQ information of %s' % comment['qq'])
            if comment['piclist'] is not None:
                pic_id_list = []
                for one_comment_pic in comment['piclist']:
                    try:
                        insert_sql = 'INSERT OR IGNORE INTO media("type", url, thumb) VALUES (?, ?, ?);'
                        cursor.execute(insert_sql,
                                       ('pic', one_comment_pic['url'], one_comment_pic['thumb']))
                        conn.commit()
                        cursor.execute('SELECT id FROM media WHERE url = ?;', (one_comment_pic['url'], ))
                        pic_id_dict = cursor.fetchone()
                        pic_id_list.append(pic_id_dict['id'])
                        logger.info('Successfully insert picture information into database')
                    except Exception:
                        logger.error('Error when trying to insert picture information into database')
                pic_id_list = str(pic_id_list)
            else:
                pic_id_list = None
            try:
                insert_sql = '''INSERT OR IGNORE INTO comment_reply(catch_time, tid, commentid, replyid, qq,
                                                          post_time, "content", picnum, piclist,
                                                          replynum)
                                VALUES (?, ?, ?, ?, ?,
                                        ?, ?, ?, ?,
                                        ?)'''
                cursor.execute(insert_sql, (parse['catch_time'], parse['tid'], comment['commentid'], 0, comment['qq'],
                                            comment['post_time'], comment['content'], comment['picnum'], pic_id_list,
                                            comment['replynum']))
                conn.commit()
                logger.info('Successfully insert comment data into database')
            except Exception:
                logger.error('Error when trying to insert comment data into database')
            if comment['reply'] is not None:
                for reply in comment['reply']:
                    cursor.execute('SELECT * FROM qq WHERE qq = ?;', (reply['qq'],))
                    qq_fetch = cursor.fetchone()
                    if qq_fetch is None:
                        try:
                            cursor.execute('INSERT INTO qq(qq, "name") VALUES (?, ?);', (reply['qq'], reply['name']))
                            conn.commit()
                            logger.info('Successfully insert QQ information of %s' % reply['qq'])
                        except Exception:
                            logger.error('Error when trying to insert QQ information of %s' % reply['qq'])
                    else:
                        if qq_fetch['name'] != reply['name']:
                            try:
                                cursor.execute('UPDATE qq SET "name" = ? WHERE qq = ?;', (reply['name'], reply['qq']))
                                conn.commit()
                                logger.info('Successfully update QQ information of %s' % reply['qq'])
                            except Exception:
                                logger.error('Error when trying to update QQ information of %s' % reply['qq'])
                    try:
                        insert_sql = '''INSERT OR IGNORE INTO comment_reply(catch_time, tid, commentid,
                                                                            replyid, qq, reply_target_qq,
                                                                            post_time, content)
                                                        VALUES (?, ?, ?,
                                                                ?, ?, ?,
                                                                ?, ?);'''
                        cursor.execute(insert_sql, (parse['catch_time'], parse['tid'], comment['commentid'],
                                                    reply['replyid'], reply['qq'], reply['reply_target_qq'],
                                                    reply['post_time'], reply['content']))
                        conn.commit()
                        logger.info('Successfully insert reply data into database')
                    except Exception:
                        logger.error('Error when trying to insert reply data into database')
    cursor.close()
    conn.close()


# noinspection PyTypeChecker
def db_write_fine(parse, db_url):
    conn = sqlite3.connect(db_url)
    logger.info('Successfully connect to SQLite database %s' % db_url)
    conn.row_factory = _dict_factory
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM qq WHERE qq = ?;', (parse['qq'],))
    qq_fetch = cursor.fetchone()
    if qq_fetch is None:
        try:
            cursor.execute('INSERT INTO qq(qq, "name") VALUES (?, ?);', (parse['qq'], parse['name']))
            conn.commit()
            logger.info('Successfully insert QQ information of %s' % parse['qq'])
        except Exception:
            logger.error('Error when trying to insert QQ information of %s' % parse['qq'])
    else:
        if qq_fetch['name'] != parse['name']:
            try:
                cursor.execute('UPDATE qq SET "name" = ? WHERE qq = ?;', (parse['name'], parse['qq']))
                conn.commit()
                logger.info('Successfully update QQ information of %s' % parse['qq'])
            except Exception:
                logger.error('Error when trying to update QQ information of %s' % parse['qq'])
    if parse['rt'] is not None:
        rt = parse['rt']
        rt_tid = rt['tid']
        cursor.execute('SELECT * FROM qq WHERE qq = ?;', (rt['qq'],))
        qq_fetch = cursor.fetchone()
        if qq_fetch is None:
            try:
                cursor.execute('INSERT INTO qq(qq, "name") VALUES (?, ?);', (rt['qq'], rt['name']))
                conn.commit()
                logger.info('Successfully insert QQ information of %s' % rt['qq'])
            except Exception:
                logger.error('Error when trying to insert QQ information of %s' % rt['qq'])
        else:
            if qq_fetch['name'] != rt['name']:
                try:
                    cursor.execute('UPDATE qq SET "name" = ? WHERE qq = ?;', (rt['name'], rt['qq']))
                    conn.commit()
                    logger.info('Successfully update QQ information of %s' % rt['qq'])
                except Exception:
                    logger.error('Error when trying to update QQ information of %s' % rt['qq'])
        if rt['piclist'] is not None:
            rt_pic_id_list = []
            for one_pic in rt['piclist']:
                if one_pic['isvideo'] == 1:
                    media_type = 'pic_video'
                else:
                    media_type = 'pic'
                try:
                    insert_sql = 'INSERT OR IGNORE INTO media("type", url, thumb) VALUES (?, ?, ?) '
                    cursor.execute(insert_sql, (media_type, one_pic['url'], one_pic['thumb']))
                    conn.commit()
                    cursor.execute('SELECT id FROM media WHERE url = ?;', (one_pic['url'],))
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
                insert_sql = 'INSERT OR IGNORE INTO media("type", url, thumb, "time") VALUES (?, ?, ?, ?);'
                cursor.execute(insert_sql, ('video', rt['video']['url'], rt['video']['thumb'], rt['video']['time']))
                conn.commit()
                cursor.execute('SELECT id FROM media WHERE url = ?;', (rt['video']['url'],))
                rt_video_id_dict = cursor.fetchone()
                rt_video_id_list.append(rt_video_id_dict['id'])
                logger.info('Successfully insert video information into database')
            except Exception:
                logger.error('Error when trying to insert video information into database')
            rt_video_id_list = str(rt_video_id_list)
        else:
            rt_video_id_list = None
        cursor.execute('SELECT * FROM rt WHERE tid = ?;', (rt['tid'],))
        rt_fetch = cursor.fetchone()
        if rt_fetch is None:
            try:
                insert_sql = '''INSERT INTO rt(tid, qq, post_time, "content", picnum,
                                                piclist, video, device, location_user, location_real,
                                                longitude, latitude, photo_time)
                                        VALUES (?, ?, ?, ?, ?,
                                                ?, ?, ?, ?, ?,
                                                ?, ?, ?);'''
                cursor.execute(insert_sql, (
                    rt['tid'], rt['qq'], rt['post_time'], rt['content'], rt['picnum'],
                    rt_pic_id_list, rt_video_id_list, rt['device'], rt['location_user'], rt['location_real'],
                    rt['longitude'], rt['latitude'], rt['photo_time']))
                conn.commit()
                logger.info('Successfully insert rt data into database')
            except Exception:
                logger.error('Error when trying to insert rt data into database')
        else:
            try:
                update_sql = '''UPDATE rt
                                      SET qq = ?, post_time = ?, "content" = ?, picnum = ?, piclist = ?,
                                          video = ?, device = ?, location_user = ?, location_real = ?,
                                          longitude = ?, latitude = ?, photo_time = ?
                                      WHERE tid = ?;'''
                cursor.execute(update_sql, (rt['qq'], rt['post_time'], rt['content'], rt['picnum'], rt_pic_id_list,
                                            rt_video_id_list, rt['device'], rt['location_user'], rt['location_real'],
                                            rt['longitude'], rt['latitude'], rt['photo_time'],
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
                insert_sql = 'INSERT OR IGNORE INTO media(type, url, thumb) VALUES (?, ?, ?);'
                cursor.execute(insert_sql, (media_type, one_pic['url'], one_pic['thumb']))
                conn.commit()
                cursor.execute('SELECT id FROM media WHERE url = ?;', (one_pic['url'],))
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
            insert_sql = 'INSERT OR IGNORE INTO media(type, url, thumb, time) VALUES (?, ?, ?, ?);'
            cursor.execute(insert_sql, ('video', parse['video']['url'], parse['video']['thumb'],
                                        parse['video']['time']))
            conn.commit()
            cursor.execute('SELECT id FROM media WHERE url = ?;', (parse['video']['url'],))
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
            insert_sql = 'INSERT OR IGNORE INTO media(type, url, time) VALUES (?, ?, ?);'
            cursor.execute(insert_sql, ('voice', parse['voice']['url'], parse['voice']['time']*1000))
            conn.commit()
            cursor.execute('SELECT id FROM media WHERE url = ?;', (parse['voice']['url'],))
            voice_id_dict = cursor.fetchone()
            voice_id_list.append(voice_id_dict['id'])
            logger.info('Successfully insert audio information into database')
        except Exception:
            logger.error('Error when trying to insert audio information into database')
        voice_id_list = str(voice_id_list)
    else:
        voice_id_list = None
    try:
        insert_sql = '''INSERT OR IGNORE INTO message(catch_time, tid, qq, post_time, rt_tid,
                                                      "content", picnum, piclist, video, voice,
                                                      device, location_user, location_real, longitude, latitude,
                                                      photo_time, viewnum, likenum, forwardnum, commentnum)
                            VALUES (?, ?, ?, ?, ?,
                                    ?, ?, ?, ?, ?,
                                    ?, ?, ?, ?, ?,
                                    ?, ?, ?, ?, ?);'''
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
                cursor.execute('INSERT OR IGNORE INTO like_person(tid, commentid, qq) VALUES (?, ?, ?);',
                               (parse['tid'], 0, likeman['qq']))
                conn.commit()
                logger.info('Successfully insert like information of tid %s' % parse['tid'])
            except Exception:
                conn.rollback()
                logger.info('Error when trying to insert like information of tid %s' % parse['tid'])
            cursor.execute('SELECT * FROM qq WHERE qq = ?;', (likeman['qq'],))
            qq_fetch = cursor.fetchone()
            if qq_fetch is None:
                try:
                    cursor.execute('INSERT INTO qq(qq, "name") VALUES (?, ?);', (likeman['qq'], likeman['name']))
                    conn.commit()
                    logger.info('Successfully insert QQ information of %s' % likeman['qq'])
                except Exception:
                    logger.error('Error when trying to insert QQ information of %s' % likeman['qq'])
            else:
                if qq_fetch['name'] != likeman['name']:
                    try:
                        cursor.execute('UPDATE qq SET "name" = ? WHERE qq = ?;', (likeman['name'], likeman['qq']))
                        conn.commit()
                        logger.info('Successfully update QQ information of %s' % likeman['qq'])
                    except Exception:
                        logger.error('Error when trying to update QQ information of %s' % likeman['qq'])
    if parse['forward'] is not None:
        for forwardman in parse['forward']:
            try:
                cursor.execute('INSERT OR IGNORE INTO forward(tid, qq) VALUES (?, ?);',
                               (parse['tid'], forwardman['qq']))
                conn.commit()
                logger.info('Successfully insert forward information of tid %s' % parse['tid'])
            except Exception:
                conn.rollback()
                logger.info('Error when trying to insert forward information of tid %s' % parse['tid'])
            cursor.execute('SELECT * FROM qq WHERE qq = ?;', (forwardman['qq'],))
            qq_fetch = cursor.fetchone()
            if qq_fetch is None:
                try:
                    cursor.execute('INSERT INTO qq(qq, "name") VALUES (?, ?);', (forwardman['qq'], forwardman['name']))
                    conn.commit()
                    logger.info('Successfully insert QQ information of %s' % forwardman['qq'])
                except Exception:
                    logger.error('Error when trying to insert QQ information of %s' % forwardman['qq'])
            else:
                if qq_fetch['name'] != forwardman['name']:
                    try:
                        cursor.execute('UPDATE qq SET "name" = ? WHERE qq = ?;', (forwardman['name'], forwardman['qq']))
                        conn.commit()
                        logger.info('Successfully update QQ information of %s' % forwardman['qq'])
                    except Exception:
                        logger.error('Error when trying to update QQ information of %s' % forwardman['qq'])
    if parse['comment'] is not None:
        for comment in parse['comment']:
            cursor.execute('SELECT * FROM qq WHERE qq = ?;', (comment['qq'],))
            qq_fetch = cursor.fetchone()
            if qq_fetch is None:
                try:
                    cursor.execute('INSERT INTO qq(qq, "name") VALUES (?, ?);', (comment['qq'], comment['name']))
                    conn.commit()
                    logger.info('Successfully insert QQ information of %s' % comment['qq'])
                except Exception:
                    logger.error('Error when trying to insert QQ information of %s' % comment['qq'])
            else:
                if qq_fetch['name'] != comment['name']:
                    try:
                        cursor.execute('UPDATE qq SET "name" = ? WHERE qq = ?;', (comment['name'], comment['qq']))
                        conn.commit()
                        logger.info('Successfully update QQ information of %s' % comment['qq'])
                    except Exception:
                        logger.error('Error when trying to update QQ information of %s' % comment['qq'])
            if comment['piclist'] is not None:
                pic_id_list = []
                for one_comment_pic in comment['piclist']:
                    try:
                        insert_sql = 'INSERT OR IGNORE INTO media("type", url, thumb) VALUES (?, ?, ?);'
                        cursor.execute(insert_sql,
                                       ('pic', one_comment_pic['url'], one_comment_pic['thumb']))
                        conn.commit()
                        cursor.execute('SELECT id FROM media WHERE url = ?;', (one_comment_pic['url'], ))
                        pic_id_dict = cursor.fetchone()
                        pic_id_list.append(pic_id_dict['id'])
                        logger.info('Successfully insert picture information into database')
                    except Exception:
                        logger.error('Error when trying to insert picture information into database')
                pic_id_list = str(pic_id_list)
            else:
                pic_id_list = None
            try:
                insert_sql = '''INSERT OR IGNORE INTO comment_reply(catch_time, tid, commentid, replyid, qq,
                                                          post_time, "content", picnum, piclist,
                                                          likenum, replynum)
                                VALUES (?, ?, ?, ?, ?,
                                        ?, ?, ?, ?,
                                        ?, ?)'''
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
                        cursor.execute('INSERT OR IGNORE INTO like_person(tid, commentid, qq) VALUES (?, ?, ?);',
                                       (parse['tid'], comment['commentid'], likeman['qq']))
                        conn.commit()
                        logger.info('Successfully insert like information of comment %s in tid %s'
                                    % (comment['commentid'], parse['tid']))
                    except Exception:
                        conn.rollback()
                        logger.info('Error when trying to insert like information of comment %s in tid %s'
                                    % (comment['commentid'], parse['tid']))
                    cursor.execute('SELECT * FROM qq WHERE qq = ?;', (likeman['qq'],))
                    qq_fetch = cursor.fetchone()
                    if qq_fetch is None:
                        try:
                            cursor.execute('INSERT INTO qq(qq, "name") VALUES (?, ?);',
                                           (likeman['qq'], likeman['name']))
                            conn.commit()
                            logger.info('Successfully insert QQ information of %s' % likeman['qq'])
                        except Exception:
                            logger.error('Error when trying to insert QQ information of %s' % likeman['qq'])
                    else:
                        if qq_fetch['name'] != likeman['name']:
                            try:
                                cursor.execute('UPDATE qq SET "name" = ? WHERE qq = ?;',
                                               (likeman['name'], likeman['qq']))
                                conn.commit()
                                logger.info('Successfully update QQ information of %s' % likeman['qq'])
                            except Exception:
                                logger.error('Error when trying to update QQ information of %s' % likeman['qq'])
            if comment['reply'] is not None:
                for reply in comment['reply']:
                    cursor.execute('SELECT * FROM qq WHERE qq = ?;', (reply['qq'],))
                    qq_fetch = cursor.fetchone()
                    if qq_fetch is None:
                        try:
                            cursor.execute('INSERT INTO qq(qq, "name") VALUES (?, ?);', (reply['qq'], reply['name']))
                            conn.commit()
                            logger.info('Successfully insert QQ information of %s' % reply['qq'])
                        except Exception:
                            logger.error('Error when trying to insert QQ information of %s' % reply['qq'])
                    else:
                        if qq_fetch['name'] != reply['name']:
                            try:
                                cursor.execute('UPDATE qq SET "name" = ? WHERE qq = ?;', (reply['name'], reply['qq']))
                                conn.commit()
                                logger.info('Successfully update QQ information of %s' % reply['qq'])
                            except Exception:
                                logger.error('Error when trying to update QQ information of %s' % reply['qq'])
                    try:
                        insert_sql = '''INSERT OR IGNORE INTO comment_reply(catch_time, tid, commentid,
                                                                            replyid, qq, reply_target_qq,
                                                                            post_time, content)
                                                        VALUES (?, ?, ?,
                                                                ?, ?, ?,
                                                                ?, ?);'''
                        cursor.execute(insert_sql, (parse['catch_time'], parse['tid'], comment['commentid'],
                                                    reply['replyid'], reply['qq'], reply['reply_target_qq'],
                                                    reply['post_time'], reply['content']))
                        conn.commit()
                        logger.info('Successfully insert reply data into database')
                    except Exception:
                        logger.error('Error when trying to insert reply data into database')
    cursor.close()
    conn.close()
