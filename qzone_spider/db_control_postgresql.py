#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" PostgreSQL connection and insert of qzone_spider """

__author__ = 'Ding Junyao'

import psycopg2
import psycopg2.extras
from qzone_spider import svar
import datetime
import logging

logger = logging.getLogger(__name__)

create_table_sql = '''
CREATE TABLE "user_loginfo" (
  "uid" SERIAL  NOT NULL,
  "email" TEXT  NOT NULL,
  "mobile"  BIGINT  NOT NULL,
  "password"  TEXT  NOT NULL,
  "nickname"  TEXT  DEFAULT NULL,
  PRIMARY KEY ("uid")
);

CREATE TABLE "target" (
  "uid" BIGINT  NOT NULL,
  "target_qq" BIGINT  NOT NULL,
  "mode"  INT NOT NULL,
  PRIMARY KEY ("uid", "target_qq")
);

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
  "sharelink" TEXT  DEFAULT NULL,
  "device"  TEXT  DEFAULT NULL,
  "location_user"  TEXT  DEFAULT NULL,
  "location_real"  TEXT  DEFAULT NULL,
  "longitude" DOUBLE PRECISION  DEFAULT NULL,
  "latitude" DOUBLE PRECISION  DEFAULT NULL,
  "altitude" DOUBLE PRECISION  DEFAULT NULL,
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
  "altitude" DOUBLE PRECISION  DEFAULT NULL,
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
  PRIMARY KEY ("tid","commentid","qq")
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
  PRIMARY KEY ("id")
);

CREATE TABLE "qq"(
  "uid" BIGINT  NOT NULL,
  "qq"  BIGINT  NOT NULL,
  "name" TEXT DEFAULT NULL,
  "memo"  TEXT  DEFAULT NULL,
  PRIMARY KEY ("uid","qq")
);

CREATE TABLE "message_memo" (
  "id"  SERIAL  NOT NULL,
  "uid"  BIGINT  NOT NULL,
  "tid" TEXT NOT NULL,
  "memo"  TEXT  NOT NULL,
  PRIMARY KEY ("id")
);

CREATE TABLE "comment_reply_memo"(
  "id"  SERIAL  NOT NULL,
  "uid"  BIGINT  NOT NULL,
  "tid" TEXT NOT NULL,
  "commentid" BIGINT NOT NULL,
  "replyid" BIGINT NOT NULL,
  "memo"  TEXT  NOT NULL,
  PRIMARY KEY ("id")
);

CREATE TABLE "media_memo" (
  "id"  SERIAL  NOT NULL,
  "uid"  BIGINT  NOT NULL,
  "media_id" BIGINT NOT NULL,
  "memo"  TEXT  NOT NULL,
  PRIMARY KEY ("id")
);
'''
# TODO: The SQL is not finished.


def db_init():
    conn = psycopg2.connect(database=svar.dbDatabase, user=svar.dbUsername, password=svar.dbPassword, host=svar.dbURL,
                            port=svar.dbPort)
    logger.info('Successfully connect to %s database %s at %s:%s'
                % (svar.dbType, svar.dbDatabase, svar.dbURL, svar.dbPort))
    cursor = conn.cursor()
    cursor.execute(create_table_sql)
    conn.commit()
    logger.info('Database initialized')
    cursor.close()
    conn.close()


def db_write_rough(parse, uid=1):
    conn = psycopg2.connect(database=svar.dbDatabase, user=svar.dbUsername, password=svar.dbPassword, host=svar.dbURL,
                            port=svar.dbPort)
    logger.info('Successfully connect to %s database %s at %s:%s'
                % (svar.dbType, svar.dbDatabase, svar.dbURL, svar.dbPort))
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if cursor.execute('SELECT * FROM qq WHERE uid = %s AND qq = %s;', (uid, parse['qq'])) == 0:
        try:
            cursor.execute('INSERT INTO qq(uid, qq, name) VALUES (%s, %s, %s);', (uid, parse['qq'], parse['name']))
            conn.commit()
            logger.info('Successfully insert QQ information of %s in uid %s' % (parse['qq'], uid))
        except Exception:
            conn.rollback()
            logger.error('Error when trying to insert QQ information of %s in uid %s' % (parse['qq'], uid))
            raise
    else:
        if cursor.fetchone()['name'] != parse['name']:
            try:
                cursor.execute('UPDATE qq SET name = %s WHERE uid = %s and qq = %s;', (parse['name'], uid, parse['qq']))
                conn.commit()
                logger.info('Successfully update QQ information of %s in uid %s' % (parse['qq'], uid))
            except Exception:
                conn.rollback()
                logger.error('Error when trying to update QQ information of %s in uid %s' % (parse['qq'], uid))
                raise
    if parse['piclist'] is not None:
        pic_id_list = []
        for one_pic in parse['piclist']:
            if one_pic['isvideo'] == 1:
                media_type = 'pic_video'
            else:
                media_type = 'pic'
            try:
                insert_sql = 'INSERT IGNORE INTO media(type,url,thumb) VALUES (%s,%s,%s);'
                cursor.execute(insert_sql, (media_type, one_pic['url'], one_pic['thumb']))
                conn.commit()
                cursor.execute('SELECT id FROM media WHERE url=%s;', one_pic['url'])
                pic_id_dict = cursor.fetchone()
                pic_id_list.append(pic_id_dict['id'])
                logger.info('Successfully insert picture information into database')
            except Exception:
                logger.error('Error when trying to insert picture information into database')
                pass
        pic_id_list = str(pic_id_list)
    else:
        pic_id_list = None

    if parse['video'] is not None:
        video_id_list = []
        try:
            insert_sql = 'INSERT IGNORE INTO media(type,url) VALUES (%s,%s);'
            cursor.execute(insert_sql, ('video', parse['video']['url']))
            conn.commit()
            cursor.execute('SELECT id FROM media WHERE url=%s;', (parse['video']['url']))
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
            insert_sql = 'INSERT INTO media("type",url,"time") VALUES (%s,%s,%s) ON CONFLICT(url) do nothing;'
            cursor.execute(insert_sql, ('voice', parse['voice']['url'], parse['voice']['time'] * 1000))
            conn.commit()
            cursor.execute('SELECT id FROM media WHERE url=%s;', (parse['voice']['url'],))
            voiceidtuple = cursor.fetchall()
            voice_id_list.append(voiceidtuple[0][0])
            logger.info('Successfully insert audio information into database')
        except Exception:
            conn.rollback()
            logger.error('Error when trying to insert audio information into database')
        voice_id_list = str(voice_id_list)
    else:
        voice_id_list = None
    if parse['photo_time'] is not None:
        phototime = datetime.datetime.fromtimestamp(parse['photo_time'])
    else:
        phototime = None
    try:
        insert_sql = '''INSERT INTO "message"(catch_time, tid, qq, post_time, rt_tid, 
                                              "content", picnum, videonum, sharelink, voice, 
                                              device, location_user, location_real, longitude, latitude, 
                                              photo_time, commentnum)
                          VALUES (%s, %s, %s,
                                  %s, %s, 
                                  %s, %s, %s, %s, %s, 
                                  %s, %s, %s, %s, %s, 
                                  %s, %s) ON CONFLICT ON CONSTRAINT message_pkey do nothing;'''
        cursor.execute(insert_sql, (
            datetime.datetime.fromtimestamp(parse['catch_time']), parse['tid'], parse['qq'],
            datetime.datetime.fromtimestamp(parse['post_time']), parse['rt_tid'],
            parse['content'], parse['picnum'], parse['videonum'], parse['sharelink'], voice_id_list,
            parse['device'], parse['location_user'], parse['location_real'], parse['longitude'], parse['latitude'],
            phototime, parse['commentnum']
        ))
        conn.commit()
        logger.info('Successfully insert data into database')
    except Exception as e:
        conn.rollback()
        logger.error('Error when trying to insert data into database')
    finally:
        cursor.close()
        conn.close()


def db_write_fine(parse):
    conn = psycopg2.connect(database=svar.dbDatabase, user=svar.dbUsername, password=svar.dbPassword, host=svar.dbURL,
                            port=svar.dbPort)
    logger.info('Successfully connect to %s database %s at %s:%s'
                % (svar.dbType, svar.dbDatabase, svar.dbURL, svar.dbPort))
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if parse['piclist'] is not None:
        pic_id_list = []
        for i in range(len(parse['piclist'])):
            if parse['piclist'][i]['isvideo'] == 1:
                media_type = 'pic_video'
            else:
                media_type = 'pic'
            try:
                insert_sql = 'INSERT INTO media("type",url,thumb) VALUES (%s,%s,%s) ON CONFLICT(url) do nothing;'
                cursor.execute(insert_sql, (media_type, parse['piclist'][i]['url'], parse['piclist'][i]['thumb']))
                conn.commit()
                cursor.execute('SELECT id FROM media WHERE url=%s;', (parse['piclist'][i]['url'],))
                picidtuple = cursor.fetchall()
                pic_id_list.append(picidtuple[0][0])
                logger.info('Successfully insert picture information into database')
            except Exception:
                conn.rollback()
                logger.error('Error when trying to insert picture information into database')
        pic_id_list = str(pic_id_list)
    else:
        pic_id_list = None
    if parse['voice'] is not None:
        voice_id_list = []
        try:
            insert_sql = 'INSERT INTO media("type",url,"time") VALUES (%s,%s,%s) ON CONFLICT(url) do nothing;'
            cursor.execute(insert_sql, ('voice', parse['voice']['url'], parse['voice']['time'] * 1000))
            conn.commit()
            cursor.execute('SELECT id FROM media WHERE url=%s;', (parse['voice']['url'], ))
            voiceidtuple = cursor.fetchall()
            voice_id_list.append(voiceidtuple[0][0])
            logger.info('Successfully insert audio information into database')
        except Exception:
            conn.rollback()
            logger.error('Error when trying to insert audio information into database')
        voice_id_list = str(voice_id_list)
    else:
        voice_id_list = None
    if parse['video'] is not None:
        video_id_list = []
        try:
            insert_sql = 'INSERT INTO media("type",url,thumb,"time") VALUES (%s,%s,%s,%s) ON CONFLICT(url) do nothing;'
            cursor.execute(insert_sql,
                           ('video', parse['video']['url'], parse['video']['thumb'], parse['video']['time']))
            conn.commit()
            cursor.execute('SELECT id FROM media WHERE url=%s;', (parse['video']['url'],))
            videoidtuple = cursor.fetchall()
            video_id_list.append(videoidtuple[0][0])
            logger.info('Successfully insert vidio information into database')
        except Exception:
            conn.rollback()
            logger.error('Error when trying to insert video information into database')
        video_id_list = str(video_id_list)
    else:
        video_id_list = None
    if parse['photo_time'] is not None:
        phototime = datetime.datetime.fromtimestamp(parse['photo_time'])
    else:
        phototime = None
    try:
        insert_sql = '''INSERT INTO "message"(catch_time, tid, qq, post_time, rt_tid, 
                                              "content", picnum, videonum, sharelink, piclist, 
                                              video, voice, device, location_user, location_real, 
                                              longitude, latitude, altitude, photo_time, viewnum, 
                                              likenum, forwardnum, commentnum)
                          VALUES (%s, %s, %s,
                                  %s, %s, 
                                  %s, %s, %s, %s, %s, 
                                  %s, %s, %s, %s, %s, 
                                  %s, %s, %s, %s, %s, 
                                  %s, %s, %s)
                          ON CONFLICT ON CONSTRAINT message_pkey do nothing;'''
        cursor.execute(insert_sql, (
            datetime.datetime.fromtimestamp(parse['catch_time']), parse['tid'], parse['qq'],
            datetime.datetime.fromtimestamp(parse['post_time']), parse['rt_tid'],
            parse['content'], parse['picnum'], parse['videonum'], parse['sharelink'], pic_id_list,
            video_id_list, voice_id_list, parse['device'], parse['location_user'], parse['location_real'],
            parse['longitude'], parse['latitude'], None, phototime, parse['viewnum'],
            parse['likenum'], parse['forwardnum'], parse['commentnum']
        ))
        conn.commit()
        logger.info('Successfully insert data into database')
    except Exception:
        conn.rollback()
        logger.error('Error when trying to insert data into database')
    finally:
        cursor.close()
        conn.close()
