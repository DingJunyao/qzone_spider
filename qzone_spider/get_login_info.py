#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Get login information of Qzone """

__author__ = 'Ding Junyao'

import time
import logging
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

login_url = 'https://qzone.qq.com/'

logger = logging.getLogger(__name__)


def _get_gtk(cookies):
    hashes = 5381
    for i in cookies['p_skey']:
        hashes += (hashes << 5) + ord(i)
    return hashes & 0x7fffffff


def account_login(qq, password, debug=False, login_try_time=2, login_wait=3, error_wait=600):
    logger.info('Trying to login with QQ and password')
    fail = 0
    while fail < login_try_time:
        mobile_emulation = {"deviceName": "Nexus 5"}
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
        if 'geteuid' in dir(os) and os.geteuid() == 0:
            chrome_options.add_argument('--no-sandbox')
        if debug:
            logger.info('''You are in debug mode. It requires GUI environment.
If you are in console without GUI environment or SSH, please exit.
If you really need it, please run it in GUI environment.
Or you need to delete the attribute 'debug=True' or related argument in %s''' % __name__)
        else:
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
        browser = webdriver.Chrome(chrome_options=chrome_options)
        try:
            browser.get(login_url)
        except Exception:
            fail += 1
            if fail == login_try_time:
                break
            logger.warning(
                '''Failed to get when getting login information of %s.
Sleep %s seconds before retrying. Remaining retry times: %s'''
                % (qq, error_wait, login_try_time - fail))
            time.sleep(error_wait)
            continue
        logger.debug("Successfully load page")
        time.sleep(login_try_time)
        try:
            access = browser.find_element_by_id('guideSkip')
            access.click()
            time.sleep(login_wait)
        except Exception:
            pass
        qq_input = browser.find_element_by_id('u')
        pass_input = browser.find_element_by_id('p')
        go = browser.find_element_by_id('go')
        qq_input.clear()
        qq_input.send_keys(qq)
        pass_input.clear()
        pass_input.send_keys(password)
        go.click()
        logger.debug("Successfully input user name and password")
        time.sleep(login_wait)
        if '验证码' in browser.page_source:
            if debug:
                # logger.warning('获取QQ为 %s 的登录信息时需要验证，请在打开的网页内进行操作' % qq)
                logger.warning(
                    'Verification needed when getting login information of %s, please check it in the browser' % qq)
            else:
                browser.quit()
                logger.error('''Verification needed when getting login information of %s.
Please add attribute 'debug=True' in %s() or related argument and rerun your application, make verification yourself.
It requires GUI environment. Once the verification made, you can change it back.
Generally speaking, you needn't do it for a long time if you use the same QQ number as spider. '''
                             % (qq, __name__))
                exit()
        if browser.title == 'QQ空间':
            cookies = {}
            for i in browser.get_cookies():
                cookies[i['name']] = i['value']
            g_qzonetoken = re.search(r'window\.shine0callback = \(function\(\){ try{return (.*?);} catch\(e\)',
                                     browser.page_source)
            browser.quit()
            gtk = _get_gtk(cookies)
            # logger.info('获取QQ为 %s 的登录信息成功' % qq)
            logger.info('Successfully get login information of %s' % qq)
            logger.debug('cookies = %s' % cookies)
            logger.debug('gtk = %s' % gtk)
            logger.debug('g_qzonetoken.group(1) = %s' % g_qzonetoken.group(1))
            return cookies, gtk, g_qzonetoken.group(1)
        else:
            fail += 1
            if fail == login_try_time:
                break
            logger.warning(
                'Fail to get login information of %s. Sleep %s seconds before retrying. Remaining retry times: %s'
                % (qq, error_wait, login_try_time - fail))
            time.sleep(error_wait)
            continue
    logger.error('Failed to get login information of %s' % qq)
    return None, None, None


def scan_login(login_try_time=2, scan_wait=20, error_wait=600):
    logger.info('Trying to login via QR Code scanning')
    fail = 0
    while fail < login_try_time:
        chrome_options = Options()
        if 'geteuid' in dir(os) and os.geteuid() == 0:
            chrome_options.add_argument('--no-sandbox')
        browser = webdriver.Chrome(chrome_options=chrome_options)
        try:
            browser.get(login_url)
        except Exception:
            fail += 1
            if fail == login_try_time:
                break
            logger.warning(
                '''Failed to get when getting login information.
Sleep %s seconds before retrying. Remaining retry times: %s'''
                % (error_wait, login_try_time - fail))
            time.sleep(error_wait)
            continue
        logger.debug('Successfully load page, please scan the QR code in %s seconds' % scan_wait)
        time.sleep(scan_wait)
        cookies = {}
        for i in browser.get_cookies():
            cookies[i['name']] = i['value']
        g_qzonetoken = re.search(r'window\.g_qzonetoken = \(function\(\){ try{return (.*?);} catch\(e\)',
                                 browser.page_source)
        gtk = _get_gtk(cookies)
        browser.quit()
        logger.info('Successfully get login information of %s' % cookies['uin'][2:])
        logger.debug('cookies = %s' % cookies)
        logger.debug('gtk = %s' % gtk)
        logger.debug('g_qzonetoken.group(1) = %s' % g_qzonetoken.group(1))
        if cookies == {} or gtk is None or g_qzonetoken.group(1) is None:
            fail += 1
            if fail == login_try_time:
                break
            logger.warning(
                'Failed to get login information. Sleep %s seconds before retrying. Remaining retry times: %s'
                % (error_wait, login_try_time - fail))
            time.sleep(error_wait)
            continue
        else:
            return cookies, gtk, g_qzonetoken.group(1)
    logger.error('Failed to get login information')
    return None, None, None
