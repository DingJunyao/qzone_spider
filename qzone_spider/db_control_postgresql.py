#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" PostgreSQL connection and insert of qzone_spider """

__author__ = 'Ding Junyao'

import psycopg2
import psycopg2.extras
import datetime
import logging

logger = logging.getLogger(__name__)

create_table_sql = '''
CREATE TABLE "message" (
  "catch_time"  TIMESTAMP NOT NULL,
  "tid" TEXT  NOT NULL,
  "qq"  BIGINT  NOT NULL,
  "post_time"  TIMESTAMP NOT NULL,
  "rt_tid"  TEXT DEFAULT NULL,
  "content" TEXT  DEFAULT NULL,
  "picnum"  SMALLINT  DEFAULT NULL,
  "piclist" TEXT  DEFAULT NULL,
  "video" TEXT  DEFAULT NULL,
  "voice" TEXT  DEFAULT NULL,
  "device"  TEXT  DEFAULT NULL,
  "location_user"  TEXT  DEFAULT NULL,
  "location_real"  TEXT  DEFAULT NULL,
  "longitude" DOUBLE PRECISION  DEFAULT NULL,
  "latitude" DOUBLE PRECISION  DEFAULT NULL,
  "photo_time"  TIMESTAMP DEFAULT NULL,
  "viewnum" BIGINT DEFAULT NULL,
  "likenum" BIGINT DEFAULT NULL,
  "forwardnum" BIGINT DEFAULT NULL,
  "commentnum" BIGINT DEFAULT NULL,
  PRIMARY KEY ("catch_time","tid")
);

CREATE TABLE "rt" (
  "tid" TEXT NOT NULL,
  "qq"  BIGINT NOT NULL,
  "post_time"  TIMESTAMP DEFAULT NULL,
  "content" TEXT DEFAULT NULL,
  "picnum"  SMALLINT  DEFAULT NULL,
  "piclist" TEXT  DEFAULT NULL,
  "video" TEXT  DEFAULT NULL,
  "device"  TEXT  DEFAULT NULL,
  "location_user"  TEXT  DEFAULT NULL,
  "location_real"  TEXT  DEFAULT NULL,
  "longitude" DOUBLE PRECISION  DEFAULT NULL,
  "latitude" DOUBLE PRECISION  DEFAULT NULL,
  "photo_time"  TIMESTAMP DEFAULT NULL,
  PRIMARY KEY ("tid")
);

CREATE TABLE "like_person"(
  "tid" TEXT NOT NULL,
  "commentid" BIGINT DEFAULT NULL,
  "qq"  BIGINT NOT NULL,
  PRIMARY KEY ("tid","commentid","qq")
);

CREATE TABLE "forward"(
  "tid" TEXT NOT NULL,
  "qq"  BIGINT NOT NULL,
  PRIMARY KEY ("tid","qq")
);

CREATE TABLE "comment_reply"(
  "catch_time"  TIMESTAMP NOT NULL,
  "tid" TEXT  NOT NULL,
  "commentid" BIGINT  NOT NULL,
  "replyid" BIGINT  NOT NULL,
  "qq"  BIGINT  NOT NULL,
  "reply_target_qq" BIGINT DEFAULT NULL,
  "post_time" TIMESTAMP NOT NULL,
  "content" TEXT  DEFAULT NULL,
  "picnum"  SMALLINT  DEFAULT NULL,
  "piclist" TEXT  DEFAULT NULL,
  "likenum" BIGINT DEFAULT NULL,
  "replynum"  BIGINT DEFAULT NULL,
  PRIMARY KEY ("catch_time","tid","commentid","replyid")
);

CREATE TABLE "media"(
  "id"  SERIAL  NOT NULL,
  "type"  TEXT  NOT NULL,
  "url" TEXT  NOT NULL UNIQUE,
  "thumb" TEXT  DEFAULT NULL,
  "time"  BIGINT  DEFAULT NULL,
  "memo"  TEXT  DEFAULT NULL,
  PRIMARY KEY ("id")
);

CREATE TABLE "qq"(
  "qq"  BIGINT  NOT NULL,
  "name" TEXT DEFAULT NULL,
  "memo"  TEXT  DEFAULT NULL,
  PRIMARY KEY ("qq")
);

CREATE TABLE "message_memo" (
  "tid" TEXT NOT NULL,
  "memo"  TEXT  NOT NULL,
  PRIMARY KEY ("tid")
);

CREATE TABLE "comment_reply_memo"(
  "tid" TEXT NOT NULL,
  "commentid" BIGINT NOT NULL,
  "replyid" BIGINT NOT NULL,
  "memo"  TEXT  NOT NULL,
  PRIMARY KEY ("tid", "commentid", "replyid", "memo")
);
'''


def db_init(db_url, db_database, db_username, db_password, db_port=5432):
    conn = psycopg2.connect(database=db_database, user=db_username, password=db_password, host=db_url, port=db_port)
    logger.info('Successfully connect to PostgreSQL database %s at %s:%s' % (db_database, db_url, db_port))
    cursor = conn.cursor()
    cursor.execute(create_table_sql)
    conn.commit()
    logger.info('Database initialized')
    cursor.close()
    conn.close()


def _timestamp_to_datetime(timestamp):
    return datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=timestamp)


def db_write_rough(parse, db_url, db_database, db_username, db_password, db_port=5432):
    conn = psycopg2.connect(database=db_database, user=db_username, password=db_password, host=db_url, port=db_port)
    logger.info('Successfully connect to PostgreSQL database %s at %s:%s' % (db_database, db_url, db_port))
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM qq WHERE qq = %s;', (parse['qq'],))
    qq_fetch = cursor.fetchone()
    if qq_fetch is None:
        try:
            cursor.execute('INSERT INTO qq(qq, "name") VALUES (%s, %s);', (parse['qq'], parse['name']))
            conn.commit()
            logger.info('Successfully insert QQ information of %s' % parse['qq'])
        except Exception:
            conn.rollback()
            logger.error('Error when trying to insert QQ information of %s' % parse['qq'])
    else:
        if qq_fetch['name'] != parse['name']:
            try:
                cursor.execute('UPDATE qq SET "name" = %s WHERE qq = %s;', (parse['name'], parse['qq']))
                conn.commit()
                logger.info('Successfully update QQ information of %s' % parse['qq'])
            except Exception:
                conn.rollback()
                logger.error('Error when trying to update QQ information of %s' % parse['qq'])
    if parse['rt'] is not None:
        rt = parse['rt']
        rt_tid = rt['tid']
        cursor.execute('SELECT * FROM qq WHERE qq = %s;', (rt['qq'],))
        qq_fetch = cursor.fetchone()
        if qq_fetch is None:
            try:
                cursor.execute('INSERT INTO qq(qq, "name") VALUES (%s, %s);', (rt['qq'], rt['name']))
                conn.commit()
                logger.info('Successfully insert QQ information of %s' % rt['qq'])
            except Exception:
                conn.rollback()
                logger.error('Error when trying to insert QQ information of %s' % rt['qq'])
        else:
            if qq_fetch['name'] != rt['name']:
                try:
                    cursor.execute('UPDATE qq SET "name" = %s WHERE qq = %s;', (rt['name'], rt['qq']))
                    conn.commit()
                    logger.info('Successfully update QQ information of %s' % rt['qq'])
                except Exception:
                    conn.rollback()
                    logger.error('Error when trying to update QQ information of %s' % rt['qq'])
        if rt['piclist'] is not None:
            rt_pic_id_list = []
            for one_pic in rt['piclist']:
                if one_pic['isvideo'] == 1:
                    media_type = 'pic_video'
                else:
                    media_type = 'pic'
                try:
                    insert_sql = '''INSERT INTO media("type", url, thumb) VALUES (%s, %s, %s)
                                      ON CONFLICT(url) do nothing;'''
                    cursor.execute(insert_sql, (media_type, one_pic['url'], one_pic['thumb']))
                    conn.commit()
                    cursor.execute('SELECT id FROM media WHERE url = %s;', (one_pic['url'], ))
                    rt_pic_id_dict = cursor.fetchone()
                    rt_pic_id_list.append(rt_pic_id_dict['id'])
                    logger.info('Successfully insert picture information into database')
                except Exception:
                    conn.rollback()
                    logger.error('Error when trying to insert picture information into database')
            rt_pic_id_list = str(rt_pic_id_list)
        else:
            rt_pic_id_list = None
        if rt['video'] is not None:
            rt_video_id_list = []
            try:
                insert_sql = 'INSERT INTO media("type", url, thumb) VALUES (%s, %s, %s) ON CONFLICT(url) do nothing;'
                cursor.execute(insert_sql, ('video', rt['video']['url'], rt['video']['thumb']))
                conn.commit()
                cursor.execute('SELECT id FROM media WHERE url = %s;', (rt['video']['url'], ))
                rt_video_id_dict = cursor.fetchone()
                rt_video_id_list.append(rt_video_id_dict['id'])
                logger.info('Successfully insert video information into database')
            except Exception:
                conn.rollback()
                logger.error('Error when trying to insert video information into database')
            rt_video_id_list = str(rt_video_id_list)
        else:
            rt_video_id_list = None
        if rt['photo_time'] is not None:
            rt_phototime = _timestamp_to_datetime(rt['photo_time'])
        else:
            rt_phototime = None
        cursor.execute('SELECT * FROM rt WHERE tid = %s;', (rt['tid'], ))
        rt_fetch = cursor.fetchone()
        if rt_fetch is None:
            try:
                insert_sql = '''INSERT INTO rt(tid, qq, "content", picnum, piclist,
                                               video, device, location_user, location_real, longitude,
                                               latitude, photo_time)
                                    VALUES (%s, %s, %s, %s, %s,
                                            %s, %s, %s, %s, %s,
                                            %s, %s);'''
                cursor.execute(insert_sql, (
                    rt['tid'], rt['qq'], rt['content'], rt['picnum'], rt_pic_id_list,
                    rt_video_id_list, rt['device'], rt['location_user'], rt['location_real'], rt['longitude'],
                    rt['latitude'], rt_phototime))
                conn.commit()
                logger.info('Successfully insert rt data into database')
            except Exception:
                conn.rollback()
                logger.error('Error when trying to insert rt data into database')
        else:
            try:
                update_sql = '''UPDATE rt
                                  SET qq = %s, "content" = %s, picnum = %s, piclist = %s, video = %s,
                                      device = %s, location_user = %s, location_real = %s, longitude = %s,
                                      latitude = %s, photo_time = %s
                                  WHERE tid = %s;'''
                cursor.execute(update_sql, (rt['qq'], rt['content'], rt['picnum'], rt_pic_id_list, rt_video_id_list,
                                            rt['device'], rt['location_user'], rt['location_real'], rt['longitude'],
                                            rt['latitude'], rt_phototime,
                                            rt['tid']))
                conn.commit()
                logger.info('Successfully update rt data into database')
            except Exception:
                conn.rollback()
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
                insert_sql = 'INSERT INTO media("type", url, thumb) VALUES (%s, %s, %s) ON CONFLICT(url) do nothing;'
                cursor.execute(insert_sql, (media_type, one_pic['url'], one_pic['thumb']))
                conn.commit()
                cursor.execute('SELECT id FROM media WHERE url = %s;', (one_pic['url'], ))
                pic_id_dict = cursor.fetchone()
                pic_id_list.append(pic_id_dict['id'])
                logger.info('Successfully insert picture information into database')
            except Exception:
                conn.rollback()
                logger.error('Error when trying to insert picture information into database')
        pic_id_list = str(pic_id_list)
    else:
        pic_id_list = None
    if parse['video'] is not None:
        video_id_list = []
        try:
            insert_sql = 'INSERT INTO media("type", url) VALUES (%s, %s) ON CONFLICT(url) do nothing;'
            cursor.execute(insert_sql, ('video', parse['video']['url']))
            conn.commit()
            cursor.execute('SELECT id FROM media WHERE url = %s;', (parse['video']['url'], ))
            video_id_dict = cursor.fetchone()
            video_id_list.append(video_id_dict['id'])
            logger.info('Successfully insert video information into database')
        except Exception:
            conn.rollback()
            logger.error('Error when trying to insert video information into database')
        video_id_list = str(video_id_list)
    else:
        video_id_list = None
    if parse['voice'] is not None:
        voice_id_list = []
        try:
            insert_sql = 'INSERT INTO media("type", url, "time") VALUES (%s, %s, %s) ON CONFLICT(url) do nothing;'
            cursor.execute(insert_sql, ('voice', parse['voice']['url'], parse['voice']['time'] * 1000))
            conn.commit()
            cursor.execute('SELECT id FROM media WHERE url = %s;', (parse['voice']['url'], ))
            voice_id_dict = cursor.fetchone()
            voice_id_list.append(voice_id_dict['id'])
            logger.info('Successfully insert audio information into database')
        except Exception:
            conn.rollback()
            logger.error('Error when trying to insert audio information into database')
        voice_id_list = str(voice_id_list)
    else:
        voice_id_list = None
    if parse['photo_time'] is not None:
        phototime = _timestamp_to_datetime(parse['photo_time'])
    else:
        phototime = None
    try:
        insert_sql = '''INSERT INTO "message"(catch_time, tid, qq,
                                              post_time, rt_tid, "content", picnum,
                                              piclist, video, voice, device, location_user, location_real,
                                              longitude, latitude, photo_time, commentnum)
                          VALUES (%s, %s, %s,
                                  %s, %s, %s, %s,
                                  %s, %s, %s, %s, %s, %s,
                                  %s, %s, %s, %s) ON CONFLICT ON CONSTRAINT message_pkey do nothing;'''
        cursor.execute(insert_sql, (
            _timestamp_to_datetime(parse['catch_time']), parse['tid'], parse['qq'],
            _timestamp_to_datetime(parse['post_time']), rt_tid, parse['content'], parse['picnum'],
            pic_id_list, video_id_list, voice_id_list, parse['device'], parse['location_user'], parse['location_real'],
            parse['longitude'], parse['latitude'], phototime, parse['commentnum']))
        conn.commit()
        logger.info('Successfully insert data into database')
    except Exception:
        conn.rollback()
        logger.error('Error when trying to insert data into database')
    if parse['comment'] is not None:
        for comment in parse['comment']:
            cursor.execute('SELECT * FROM qq WHERE qq = %s;', (comment['qq'],))
            qq_fetch = cursor.fetchone()
            if qq_fetch is None:
                try:
                    cursor.execute('INSERT INTO qq(qq, "name") VALUES (%s, %s);',
                                   (comment['qq'], comment['name']))
                    conn.commit()
                    logger.info('Successfully insert QQ information of %s' % comment['qq'])
                except Exception:
                    conn.rollback()
                    logger.error('Error when trying to insert QQ information of %s' % comment['qq'])
            else:
                if qq_fetch['name'] != comment['name']:
                    try:
                        cursor.execute(
                            'UPDATE qq SET "name" = %s WHERE qq = %s;',
                            (comment['name'], comment['qq']))
                        conn.commit()
                        logger.info('Successfully update QQ information of %s' % comment['qq'])
                    except Exception:
                        conn.rollback()
                        logger.error('Error when trying to update QQ information of %s' % comment['qq'])
            if comment['piclist'] is not None:
                pic_id_list = []
                for one_comment_pic in comment['piclist']:
                    try:
                        insert_sql = '''INSERT INTO media("type", url, thumb) VALUES (%s, %s, %s)
                                          ON CONFLICT(url) do nothing;'''
                        cursor.execute(insert_sql,
                                       ('pic', one_comment_pic['url'], one_comment_pic['thumb']))
                        conn.commit()
                        cursor.execute('SELECT id FROM media WHERE url = %s;', (one_comment_pic['url'], ))
                        pic_id_dict = cursor.fetchone()
                        pic_id_list.append(pic_id_dict['id'])
                        logger.info('Successfully insert picture information into database')
                    except Exception:
                        conn.rollback()
                        logger.error('Error when trying to insert picture information into database')
                pic_id_list = str(pic_id_list)
            else:
                pic_id_list = None
            try:
                insert_sql = '''INSERT INTO comment_reply(catch_time, tid,
                                                          commentid, replyid, qq,
                                                          post_time, "content",
                                                          picnum, piclist, replynum)
                                VALUES (%s, %s,
                                        %s, %s, %s,
                                        %s, %s,
                                        %s, %s, %s) ON CONFLICT ON CONSTRAINT comment_reply_pkey do nothing;'''
                cursor.execute(insert_sql, (_timestamp_to_datetime(parse['catch_time']), parse['tid'],
                                            comment['commentid'], 0, comment['qq'],
                                            _timestamp_to_datetime(comment['post_time']), comment['content'],
                                            comment['picnum'], pic_id_list, comment['replynum']))
                conn.commit()
                logger.info('Successfully insert comment data into database')
            except Exception:
                conn.rollback()
                logger.error('Error when trying to insert comment data into database')
            if comment['reply'] is not None:
                for reply in comment['reply']:
                    cursor.execute('SELECT * FROM qq WHERE qq = %s;', (reply['qq'],))
                    qq_fetch = cursor.fetchone()
                    if qq_fetch is None:
                        try:
                            cursor.execute('INSERT INTO qq(qq, "name") VALUES (%s, %s);', (reply['qq'], reply['name']))
                            conn.commit()
                            logger.info('Successfully insert QQ information of %s' % reply['qq'])
                        except Exception:
                            conn.rollback()
                            logger.error('Error when trying to insert QQ information of %s' % reply['qq'])
                    else:
                        if qq_fetch['name'] != reply['name']:
                            try:
                                cursor.execute('UPDATE qq SET "name" = %s WHERE qq = %s;', (reply['name'], reply['qq']))
                                conn.commit()
                                logger.info('Successfully update QQ information of %s' % reply['qq'])
                            except Exception:
                                conn.rollback()
                                logger.error('Error when trying to update QQ information of %s' % reply['qq'])
                    try:
                        insert_sql = '''INSERT INTO comment_reply(catch_time, tid, commentid,
                                                                   replyid, qq, reply_target_qq, post_time, content)
                                                        VALUES (%s, %s,
                                                                %s, %s, %s,
                                                                %s,
                                                                %s,
                                                                %s)
                                                        ON CONFLICT ON CONSTRAINT comment_reply_pkey do nothing;'''
                        cursor.execute(insert_sql, (_timestamp_to_datetime(parse['catch_time']), parse['tid'],
                                                    comment['commentid'], reply['replyid'], reply['qq'],
                                                    reply['reply_target_qq'],
                                                    _timestamp_to_datetime(reply['post_time']),
                                                    reply['content']))
                        conn.commit()
                        logger.info('Successfully insert reply data into database')
                    except Exception:
                        conn.rollback()
                        logger.error('Error when trying to insert reply data into database')
    cursor.close()
    conn.close()


def db_write_fine(parse, db_url, db_database, db_username, db_password, db_port=5432):
    conn = psycopg2.connect(database=db_database, user=db_username, password=db_password, host=db_url, port=db_port)
    logger.info('Successfully connect to PostgreSQL database %s at %s:%s' % (db_database, db_url, db_port))
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM qq WHERE qq = %s;', (parse['qq'],))
    qq_fetch = cursor.fetchone()
    if qq_fetch is None:
        try:
            cursor.execute('INSERT INTO qq(qq, "name") VALUES (%s, %s);', (parse['qq'], parse['name']))
            conn.commit()
            logger.info('Successfully insert QQ information of %s' % parse['qq'])
        except Exception:
            conn.rollback()
            logger.error('Error when trying to insert QQ information of %s' % parse['qq'])
    else:
        if qq_fetch['name'] != parse['name']:
            try:
                cursor.execute('UPDATE qq SET "name" = %s WHERE qq = %s;', (parse['name'], parse['qq']))
                conn.commit()
                logger.info('Successfully update QQ information of %s' % parse['qq'])
            except Exception:
                conn.rollback()
                logger.error('Error when trying to update QQ information of %s' % parse['qq'])
    if parse['rt'] is not None:
        rt = parse['rt']
        rt_tid = rt['tid']
        cursor.execute('SELECT * FROM qq WHERE qq = %s;', (rt['qq'],))
        qq_fetch = cursor.fetchone()
        if qq_fetch is None:
            try:
                cursor.execute('INSERT INTO qq(qq, "name") VALUES (%s, %s);', (rt['qq'], rt['name']))
                conn.commit()
                logger.info('Successfully insert QQ information of %s' % rt['qq'])
            except Exception:
                conn.rollback()
                logger.error('Error when trying to insert QQ information of %s' % rt['qq'])
        else:
            if qq_fetch['name'] != rt['name']:
                try:
                    cursor.execute('UPDATE qq SET "name" = %s WHERE qq = %s;', (rt['name'], rt['qq']))
                    conn.commit()
                    logger.info('Successfully update QQ information of %s' % rt['qq'])
                except Exception:
                    conn.rollback()
                    logger.error('Error when trying to update QQ information of %s' % rt['qq'])
        if rt['piclist'] is not None:
            rt_pic_id_list = []
            for one_pic in rt['piclist']:
                if one_pic['isvideo'] == 1:
                    media_type = 'pic_video'
                else:
                    media_type = 'pic'
                try:
                    insert_sql = '''INSERT INTO media("type", url, thumb) VALUES (%s, %s, %s)
                                          ON CONFLICT(url) do nothing;'''
                    cursor.execute(insert_sql, (media_type, one_pic['url'], one_pic['thumb']))
                    conn.commit()
                    cursor.execute('SELECT id FROM media WHERE url = %s;', (one_pic['url'],))
                    rt_pic_id_dict = cursor.fetchone()
                    rt_pic_id_list.append(rt_pic_id_dict['id'])
                    logger.info('Successfully insert picture information into database')
                except Exception:
                    conn.rollback()
                    logger.error('Error when trying to insert picture information into database')
            rt_pic_id_list = str(rt_pic_id_list)
        else:
            rt_pic_id_list = None
        if rt['video'] is not None:
            rt_video_id_list = []
            try:
                insert_sql = '''INSERT INTO media("type", url, thumb, "time") VALUES (%s, %s, %s, %s)
                                  ON CONFLICT(url) do nothing;'''
                cursor.execute(insert_sql, ('video', rt['video']['url'], rt['video']['thumb'], rt['video']['time']))
                conn.commit()
                cursor.execute('SELECT id FROM media WHERE url = %s;', (rt['video']['url'],))
                rt_video_id_dict = cursor.fetchone()
                rt_video_id_list.append(rt_video_id_dict['id'])
                logger.info('Successfully insert video information into database')
            except Exception:
                conn.rollback()
                logger.error('Error when trying to insert video information into database')
            rt_video_id_list = str(rt_video_id_list)
        else:
            rt_video_id_list = None
        if rt['photo_time'] is not None:
            rt_phototime = _timestamp_to_datetime(rt['photo_time'])
        else:
            rt_phototime = None
        cursor.execute('SELECT * FROM rt WHERE tid = %s;', (rt['tid'],))
        rt_fetch = cursor.fetchone()
        if rt_fetch is None:
            try:
                insert_sql = '''INSERT INTO rt(tid, qq, post_time, "content", picnum,
                                               piclist, video, device, location_user, location_real,
                                               longitude, latitude, photo_time)
                                        VALUES (%s, %s, %s, %s, %s,
                                                %s, %s, %s, %s, %s,
                                                %s, %s, %s);'''
                cursor.execute(insert_sql, (
                    rt['tid'], rt['qq'], _timestamp_to_datetime(rt['post_time']), rt['content'], rt['picnum'],
                    rt_pic_id_list, rt_video_id_list, rt['device'], rt['location_user'], rt['location_real'],
                    rt['longitude'], rt['latitude'], rt_phototime))
                conn.commit()
                logger.info('Successfully insert rt data into database')
            except Exception:
                conn.rollback()
                logger.error('Error when trying to insert rt data into database')
        else:
            try:
                update_sql = '''UPDATE rt
                                      SET qq = %s, post_time = %s, "content" = %s,
                                          picnum = %s, piclist = %s, video = %s, device = %s,
                                          location_user = %s, location_real = %s, longitude = %s, latitude = %s,
                                          photo_time = %s
                                      WHERE tid = %s;'''
                cursor.execute(update_sql, (rt['qq'], _timestamp_to_datetime(rt['post_time']), rt['content'],
                                            rt['picnum'], rt_pic_id_list, rt_video_id_list, rt['device'],
                                            rt['location_user'], rt['location_real'], rt['longitude'], rt['latitude'],
                                            rt_phototime, rt['tid']))
                conn.commit()
                logger.info('Successfully update rt data into database')
            except Exception:
                conn.rollback()
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
                insert_sql = 'INSERT INTO media("type", url, thumb) VALUES (%s, %s, %s) ON CONFLICT(url) do nothing;'
                cursor.execute(insert_sql, (media_type, one_pic['url'], one_pic['thumb']))
                conn.commit()
                cursor.execute('SELECT id FROM media WHERE url = %s;', (one_pic['url'],))
                pic_id_dict = cursor.fetchone()
                pic_id_list.append(pic_id_dict['id'])
                logger.info('Successfully insert picture information into database')
            except Exception:
                conn.rollback()
                logger.error('Error when trying to insert picture information into database')
        pic_id_list = str(pic_id_list)
    else:
        pic_id_list = None
    if parse['video'] is not None:
        video_id_list = []
        try:
            insert_sql = '''INSERT INTO media("type", url, thumb, "time") VALUES (%s, %s, %s, %s)
                              ON CONFLICT(url) do nothing;'''
            cursor.execute(insert_sql,
                           ('video', parse['video']['url'], parse['video']['thumb'], parse['video']['time']))
            conn.commit()
            cursor.execute('SELECT id FROM media WHERE url=%s;', (parse['video']['url'],))
            video_id_dict = cursor.fetchone()
            video_id_list.append(video_id_dict['id'])
            logger.info('Successfully insert video information into database')
        except Exception:
            conn.rollback()
            logger.error('Error when trying to insert video information into database')
        video_id_list = str(video_id_list)
    else:
        video_id_list = None
    if parse['voice'] is not None:
        voice_id_list = []
        try:
            insert_sql = 'INSERT INTO media("type", url, "time") VALUES (%s, %s, %s) ON CONFLICT(url) do nothing;'
            cursor.execute(insert_sql, ('voice', parse['voice']['url'], parse['voice']['time'] * 1000))
            conn.commit()
            cursor.execute('SELECT id FROM media WHERE url = %s;', (parse['voice']['url'], ))
            voice_id_dict = cursor.fetchone()
            voice_id_list.append(voice_id_dict['id'])
            logger.info('Successfully insert audio information into database')
        except Exception:
            conn.rollback()
            logger.error('Error when trying to insert audio information into database')
        voice_id_list = str(voice_id_list)
    else:
        voice_id_list = None
    if parse['photo_time'] is not None:
        phototime = _timestamp_to_datetime(parse['photo_time'])
    else:
        phototime = None
    try:
        insert_sql = '''INSERT INTO "message"(catch_time, tid, qq,
                                              post_time, rt_tid, "content", picnum, piclist,
                                              video, voice, device, location_user, location_real,
                                              longitude, latitude, photo_time, viewnum, likenum,
                                              forwardnum, commentnum)
                          VALUES (%s, %s, %s,
                                  %s, %s, %s, %s, %s,
                                  %s, %s, %s, %s, %s,
                                  %s, %s, %s, %s, %s,
                                  %s, %s)
                          ON CONFLICT ON CONSTRAINT message_pkey do nothing;'''
        cursor.execute(insert_sql, (
            _timestamp_to_datetime(parse['catch_time']), parse['tid'], parse['qq'],
            _timestamp_to_datetime(parse['post_time']), rt_tid, parse['content'], parse['picnum'], pic_id_list,
            video_id_list, voice_id_list, parse['device'], parse['location_user'], parse['location_real'],
            parse['longitude'], parse['latitude'], phototime, parse['viewnum'],  parse['likenum'],
            parse['forwardnum'], parse['commentnum']))
        conn.commit()
        logger.info('Successfully insert data into database')
    except Exception:
        conn.rollback()
        logger.error('Error when trying to insert data into database')
    if parse['like'] is not None:
        for likeman in parse['like']:
            try:
                cursor.execute('''INSERT INTO like_person(tid, commentid, qq) VALUES (%s, %s, %s)
                                    ON CONFLICT ON CONSTRAINT like_person_pkey do nothing;''',
                               (parse['tid'], 0, likeman['qq']))
                conn.commit()
                logger.info('Successfully insert like information of tid %s' % parse['tid'])
            except Exception:
                conn.rollback()
                logger.info('Error when trying to insert like information of tid %s' % parse['tid'])
            cursor.execute('SELECT * FROM qq WHERE qq = %s;', (likeman['qq'],))
            qq_fetch = cursor.fetchone()
            if qq_fetch is None:
                try:
                    cursor.execute('INSERT INTO qq(qq, "name") VALUES (%s, %s);', (likeman['qq'], likeman['name']))
                    conn.commit()
                    logger.info('Successfully insert QQ information of %s' % likeman['qq'])
                except Exception:
                    conn.rollback()
                    logger.error('Error when trying to insert QQ information of %s' % likeman['qq'])
            else:
                if qq_fetch['name'] != likeman['name']:
                    try:
                        cursor.execute('UPDATE qq SET "name" = %s WHERE qq = %s;', (likeman['name'], likeman['qq']))
                        conn.commit()
                        logger.info('Successfully update QQ information of %s' % likeman['qq'])
                    except Exception:
                        conn.rollback()
                        logger.error('Error when trying to update QQ information of %s' % likeman['qq'])
    if parse['forward'] is not None:
        for forwardman in parse['forward']:
            try:
                cursor.execute('''INSERT INTO forward(tid, qq) VALUES (%s, %s)
                                    ON CONFLICT ON CONSTRAINT forward_pkey do nothing;''',
                               (parse['tid'], forwardman['qq']))
                conn.commit()
                logger.info('Successfully insert forward information of tid %s' % parse['tid'])
            except Exception:
                conn.rollback()
                logger.info('Error when trying to insert forward information of tid %s' % parse['tid'])
            cursor.execute('SELECT * FROM qq WHERE qq = %s;', (forwardman['qq'],))
            qq_fetch = cursor.fetchone()
            if qq_fetch is None:
                try:
                    cursor.execute('INSERT INTO qq(qq, "name") VALUES (%s, %s);',
                                   (forwardman['qq'], forwardman['name']))
                    conn.commit()
                    logger.info('Successfully insert QQ information of %s' % forwardman['qq'])
                except Exception:
                    conn.rollback()
                    logger.error('Error when trying to insert QQ information of %s' % forwardman['qq'])
            else:
                if qq_fetch['name'] != forwardman['name']:
                    try:
                        cursor.execute('UPDATE qq SET "name" = %s WHERE qq = %s;',
                                       (forwardman['name'], forwardman['qq']))
                        conn.commit()
                        logger.info('Successfully update QQ information of %s' % forwardman['qq'])
                    except Exception:
                        conn.rollback()
                        logger.error('Error when trying to update QQ information of %s' % forwardman['qq'])
    if parse['comment'] is not None:
        for comment in parse['comment']:
            cursor.execute('SELECT * FROM qq WHERE qq = %s;', (comment['qq'],))
            qq_fetch = cursor.fetchone()
            if qq_fetch is None:
                try:
                    cursor.execute('INSERT INTO qq(qq, "name") VALUES (%s, %s);', (comment['qq'], comment['name']))
                    conn.commit()
                    logger.info('Successfully insert QQ information of %s' % comment['qq'])
                except Exception:
                    conn.rollback()
                    logger.error('Error when trying to insert QQ information of %s' % comment['qq'])
            else:
                if qq_fetch['name'] != comment['name']:
                    try:
                        cursor.execute(
                            'UPDATE qq SET "name" = %s WHERE qq = %s;', (comment['name'], comment['qq']))
                        conn.commit()
                        logger.info('Successfully update QQ information of %s' % comment['qq'])
                    except Exception:
                        conn.rollback()
                        logger.error('Error when trying to update QQ information of %s' % comment['qq'])
            if comment['piclist'] is not None:
                pic_id_list = []
                for one_comment_pic in comment['piclist']:
                    try:
                        insert_sql = '''INSERT INTO media("type", url, thumb) VALUES (%s, %s, %s)
                                          ON CONFLICT(url) do nothing;'''
                        cursor.execute(insert_sql,
                                       ('pic', one_comment_pic['url'], one_comment_pic['thumb']))
                        conn.commit()
                        cursor.execute('SELECT id FROM media WHERE url = %s;', (one_comment_pic['url'], ))
                        pic_id_dict = cursor.fetchone()
                        pic_id_list.append(pic_id_dict['id'])
                        logger.info('Successfully insert picture information into database')
                    except Exception:
                        conn.rollback()
                        logger.error('Error when trying to insert picture information into database')
                pic_id_list = str(pic_id_list)
            else:
                pic_id_list = None
            try:
                insert_sql = '''INSERT INTO comment_reply(catch_time, tid,
                                                          commentid, replyid, qq,
                                                          post_time, "content",
                                                          picnum, piclist, likenum, replynum)
                                VALUES (%s, %s,
                                        %s, %s, %s,
                                        %s, %s,
                                        %s, %s, %s) ON CONFLICT ON CONSTRAINT comment_reply_pkey do nothing;'''
                cursor.execute(insert_sql, (_timestamp_to_datetime(parse['catch_time']), parse['tid'],
                                            comment['commentid'], 0, comment['qq'],
                                            _timestamp_to_datetime(comment['post_time']), comment['content'],
                                            comment['picnum'], pic_id_list, comment['likenum'], comment['replynum']))
                conn.commit()
                logger.info('Successfully insert comment data into database')
            except Exception:
                conn.rollback()
                logger.error('Error when trying to insert comment data into database')
            if comment['like'] is not None:
                for likeman in comment['like']:
                    try:
                        cursor.execute('''INSERT INTO like_person(tid, commentid, qq) VALUES (%s, %s, %s)
                                            ON CONFLICT ON CONSTRAINT like_person_pkey do nothing;''',
                                       (parse['tid'], comment['commentid'], likeman['qq']))
                        conn.commit()
                        logger.info('Successfully insert like information of comment %s in tid %s'
                                    % (comment['commentid'], parse['tid']))
                    except Exception:
                        conn.rollback()
                        logger.info('Error when trying to insert like information of comment %s in tid %s'
                                    % (comment['commentid'], parse['tid']))
                    cursor.execute('SELECT * FROM qq WHERE qq = %s;', (likeman['qq'],))
                    qq_fetch = cursor.fetchone()
                    if qq_fetch is None:
                        try:
                            cursor.execute('INSERT INTO qq(qq, "name") VALUES (%s, %s);',
                                           (likeman['qq'], likeman['name']))
                            conn.commit()
                            logger.info('Successfully insert QQ information of %s' % likeman['qq'])
                        except Exception:
                            conn.rollback()
                            logger.error(
                                'Error when trying to insert QQ information of %s' % likeman['qq'])
                    else:
                        if qq_fetch['name'] != likeman['name']:
                            try:
                                cursor.execute(
                                    'UPDATE qq SET "name" = %s WHERE qq = %s;', (likeman['name'], likeman['qq']))
                                conn.commit()
                                logger.info('Successfully update QQ information of %s' % likeman['qq'])
                            except Exception:
                                conn.rollback()
                                logger.error('Error when trying to update QQ information of %s' % likeman['qq'])
            if comment['reply'] is not None:
                for reply in comment['reply']:
                    cursor.execute('SELECT * FROM qq WHERE qq = %s;', (reply['qq'],))
                    qq_fetch = cursor.fetchone()
                    if qq_fetch is None:
                        try:
                            cursor.execute('INSERT INTO qq(qq, "name") VALUES (%s, %s);', (reply['qq'], reply['name']))
                            conn.commit()
                            logger.info('Successfully insert QQ information of %s' % reply['qq'])
                        except Exception:
                            conn.rollback()
                            logger.error('Error when trying to insert QQ information of %s' % reply['qq'])
                    else:
                        if qq_fetch['name'] != reply['name']:
                            try:
                                cursor.execute('UPDATE qq SET "name" = %s WHERE qq = %s;', (reply['name'], reply['qq']))
                                conn.commit()
                                logger.info('Successfully update QQ information of %s' % reply['qq'])
                            except Exception:
                                conn.rollback()
                                logger.error('Error when trying to update QQ information of %s' % reply['qq'])
                    try:
                        insert_sql = '''INSERT INTO comment_reply(catch_time, tid, commentid,
                                                                   replyid, qq, reply_target_qq, post_time, content)
                                                        VALUES (%s, %s,
                                                                %s, %s, %s,
                                                                %s,
                                                                %s,
                                                                %s)
                                                        ON CONFLICT ON CONSTRAINT comment_reply_pkey do nothing;'''
                        cursor.execute(insert_sql, (_timestamp_to_datetime(parse['catch_time']), parse['tid'],
                                                    comment['commentid'], reply['replyid'], reply['qq'],
                                                    reply['reply_target_qq'],
                                                    _timestamp_to_datetime(reply['post_time']),
                                                    reply['content']))
                        conn.commit()
                        logger.info('Successfully insert reply data into database')
                    except Exception:
                        conn.rollback()
                        logger.error('Error when trying to insert reply data into database')
    cursor.close()
    conn.close()
