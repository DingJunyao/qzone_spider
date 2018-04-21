#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Get login information of Qzone """

__author__ = 'Ding Junyao (Rewrite from LiuXingMing and doctorwho77)'

import time
import logging
import re
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from qzone_spider import svar

'''
Rewrite From:

https://github.com/LiuXingMing/QQSpider
https://github.com/doctorwho77/qq_mood

In:
QQ
Password

Out:
Cookies
qzonetoken
GTK
'''

logger = logging.getLogger(__name__)


def get_gtk(cookies):
    hashes = 5381
    for letter in cookies['p_skey']:
        hashes += (hashes << 5) + ord(letter)
    return hashes & 0x7fffffff


def account_login(qq, password):
    # logger.info('开始尝试通过账号密码登录')
    logger.info('Trying to login with QQ and password')
    fail = 0
    while fail < svar.loginFailTime:
        # try:
        mobile_emulation = {"deviceName": "Nexus 5"}
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        browser = webdriver.Chrome(chrome_options=chrome_options)
        # browser.set_page_load_timeout(svar.pageWaitTime)
        '''try:
            browser.get(svar.login_URL)
        except TimeoutException:
            # logger.warning('打开网页超过 %s 秒，即将停止加载，接下来的操作可能会发生异常' % svar.pageWaitTime)
            browser.execute_script('window.stop()')
        logger.debug("网页加载成功")
        try:
            access = browser.find_element_by_id('guideSkip')
            access.click()
            time.sleep(svar.loginWaitTime)
        except Exception:
            pass
        '''
        browser.get(svar.login_URL)
        # logger.debug("网页加载成功")
        logger.debug("Successfully load page")
        time.sleep(svar.loginWaitTime)
        try:
            access = browser.find_element_by_id('guideSkip')
            access.click()
            time.sleep(svar.loginWaitTime)
        except Exception:
            pass
        qq_input = browser.find_element_by_id('u')
        pass_input = browser.find_element_by_id('p')
        go = browser.find_element_by_id('go')
        qq_input.clear()
        pass_input.clear()
        qq_input.send_keys(qq)
        pass_input.send_keys(password)
        go.click()
        # logger.debug("用户名和密码输入成功")
        logger.debug("Successfully input user name and password")
        time.sleep(svar.loginWaitTime)
        while '验证码' in browser.page_source:  # TODO: 现在的验证码是拖动图片完成的，目前的做法是手工完成，未来将考虑自动完成
            try:
                # logger.warning('获取QQ为 %s 的登录信息时需要验证，请在打开的网页内进行操作' % qq)
                logger.warning('Verification needed when getting login information of %s, please verify in the window' % qq)
                browser.save_screenshot('verification.png')
                im = Image.open('verification.png')
                im.show()
                time.sleep(svar.scanWaitTime)
                if not svar.verification:
                    # break
                    pass
                '''
                iframes = browser.find_elements_by_tag_name('iframe')
                try:
                    browser.switch_to.frame(iframes[1])
                    vcode_input = browser.find_element_by_id('cap_input')
                    submit = browser.find_element_by_id('verify_btn')
                    vcode = input("请输入验证码：") 
                    print("Verification code is: " + vcode)
                    vcode_input.clear()
                    vcode_input.send_keys(vcode)
                    submit.click()
                    time.sleep(svar.loginWaitTime)
                except Exception:
                    break
                '''
            except Exception:
                browser.quit()
                return ''
        if browser.title == 'QQ空间':
            cookie = {}
            for elem in browser.get_cookies():
                cookie[elem['name']] = elem['value']
            html = browser.page_source
            g_qzonetoken = re.search(r'window\.shine0callback = \(function\(\)\{ try\{return (.*?);\} catch\(e\)', html)
            browser.quit()
            gtk = get_gtk(cookie)
            # logger.info('获取QQ为 %s 的登录信息成功' % qq)
            logger.info('Successfully get login information of %s' % qq)
            logger.debug('cookie = %s' % cookie)
            logger.debug('gtk = %s' % gtk)
            logger.debug('g_qzonetoken.group(1) = %s' % g_qzonetoken.group(1))
            return cookie, gtk, g_qzonetoken.group(1)
        else:
            # logger.error('获取QQ为 %s 的登录信息失败' % qq)
            logger.error('Fail to get login information of %s' % qq)
            return '', '', ''
    return '', '', ''


def scan_login():
    # logger.info('开始尝试通过扫码登录')
    logger.info('Trying to login by scanning QR code')
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--start-maximized')
    browser = webdriver.Chrome(chrome_options=chrome_options)
    # browser.set_page_load_timeout(svar.pageWaitTime)
    '''try:
        browser.get(svar.login_URL)
    except TimeoutException:
        logger.warning('打开网页超过 %s 秒，即将停止加载，接下来的操作可能会发生异常')
        # browser.execute_script('window.stop()')'''
    browser.get(svar.login_URL)
    time.sleep(svar.loginWaitTime)
    # logger.debug('打开网页成功，即将截图，请在 %s 秒内进行扫码' % svar.scanWaitTime)
    logger.debug('Successfully load page, a screenshot will be taken, please scan the QR code in %s seconds' % svar.scanWaitTime)
    browser.get_screenshot_as_file('QR.png')
    im = Image.open('QR.png')
    im.show()
    time.sleep(svar.scanWaitTime)
    cookie = {}
    for elem in browser.get_cookies():
        cookie[elem['name']] = elem['value']
    html = browser.page_source
    g_qzonetoken = re.search(r'window\.g_qzonetoken = \(function\(\)\{ try\{return (.*?);\} catch\(e\)', html)
    gtk = get_gtk(cookie)
    browser.quit()
    logger.info('Successfully get login information of %s' % cookie['uin'][2:])
    logger.debug('cookie = %s' % cookie)
    logger.debug('gtk = %s' % gtk)
    logger.debug('g_qzonetoken.group(1) = %s' % g_qzonetoken.group(1))
    return cookie, gtk, g_qzonetoken.group(1)
