#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------
# @ File       : utils.py
# @ Description:  
# @ Author     : Alex Chung
# @ Contact    : yonganzhong@outlook.com
# @ License    : Copyright (c) 2017-2018
# @ Time       : 2020/6/28 下午5:34
# @ Software   : PyCharm
#-------------------------------------------------------
import re
import time

def process_title(title):
    """

    :param title:
    :return:
    """
    if len(title)>=1:
        title = title[0].strip()
        # remove \n\t and space
        # title = ''.join([t.group() for t in title])
        title = title.replace('\n', '')
        title = title.replace('\t', '')
        title = title.replace(' ', '')

    else:
        title = ''
    return title

def process_label(labels):
    """

    :param labels:
    :return:
    """
    if len(labels) >=1:
        label = ",".join([label.strip() for label in labels])
    else:
        label = ''
    return label

def process_content(contents):
    """

    :param contents:
    :return:
    """

    content = '\n'.join([content.strip() for content in contents if content != ''])


    return content


def process_time(local_time, is_stamp=True):
    """

    :param local_time:
    :return:
    """
    if isinstance(local_time, list):
        local_time = ' '.join(local_time)
    if local_time is None:
        local_time = "1970-01-01 08:00:00"
    local_time = local_time.replace('：', ':')
    local_time = local_time.replace('年', '-')
    local_time = local_time.replace('月', '-')
    local_time = local_time.replace('日', ' ')
    time_date = re.findall(r'\d{4}-\d{1,2}-\d{1,2}', local_time)
    time_second = re.findall(r'\d{1,2}:\d{1,2}:\d{1,2}', local_time)

    if len(time_date) == 0:
        local_time = "1970-01-01 08:00:00"
    else:
        if len(time_second) > 0:
            local_time = f'{time_date[0]} {time_second[0]}'
        else:
            local_time = f"{time_date[0]} 00:00:00"

    if is_stamp:
        struct_time = time.strptime(local_time, "%Y-%m-%d %H:%M:%S")
        stamp = str(int(time.mktime(struct_time)))
        return stamp
    else:
        return local_time


def convert_stamp_time(time_stamp, is_date=False):
    """
    convert stamp to time
    :param time_stamp:
    :param is_date:
    :return:
    """
    local_time = time.localtime(int(time_stamp))
    format_time = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
    if is_date:
        format_time = format_time.split(' ')[0]
    return format_time


def scroll(driver, height_ratio=None, sleep_time=0.1):
    # function to handle dynamic page content loading - using Selenium
    # define initial page height for 'while' loop
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            break
        else:
            last_height = new_height
    
    if height_ratio is not None:
        last_height = int(last_height * height_ratio)

    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(sleep_time)
    height = last_height / 6
    driver.execute_script("window.scrollTo(0, {0});".format(height))
    time.sleep(sleep_time)
    driver.execute_script("window.scrollTo(0, {0});".format(height * 2))
    time.sleep(sleep_time)
    driver.execute_script("window.scrollTo(0, {0});".format(height * 3))
    time.sleep(sleep_time)
    driver.execute_script("window.scrollTo(0, {0});".format(height * 4))
    time.sleep(sleep_time)
    driver.execute_script("window.scrollTo(0, {0});".format(height * 5))
    time.sleep(sleep_time)
    driver.execute_script("window.scrollTo(0, {0});".format(last_height))
    time.sleep(sleep_time)

    return last_height
