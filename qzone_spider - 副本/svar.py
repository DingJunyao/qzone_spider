#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Define the variables of the qzone_spider. """

__author__ = 'Ding Junyao'

browserPath = 'D:\\Code\\qzone_analyse\\qzone_analyse\\bin\\chromedriver.exe'
LoginUA = 'Mozilla/5.0 (Linux; U; Android 2.3.6; en-us; Nexus S Build/GRK39F) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1'
browserUA = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0'
requestHeader = {
    'Host': 'h5.qzone.qq.com',
    'User-Agent': browserUA,
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://user.qzone.qq.com/***REMOVED***?_t_=0.22746974226377736',
    'Connection': 'keep-alive'
}

login_URL = 'https://qzone.qq.com/'
scanLogin = False
loginWaitTime = 3
scanWaitTime = 20
pageWaitTime = 10
spiderWaitTime = 5

roughJSON_URL = 'https://h5.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6'
fineJSON_URL = 'https://h5.qzone.qq.com/webapp/json/mqzone_detail/shuoshuo'

dbType = 'MySQL'
dbURL = 'localhost'  # '***REMOVED***'
dbPort = 3306  # 3306
dbUsername = 'root'
dbPassword = 'root'
dbDatabase = 'mood2'

verification = True

loginFailTime = 2
getRoughDataFailTime = 2
getFineDataFailTime = 2

errorWaitTime = 600
