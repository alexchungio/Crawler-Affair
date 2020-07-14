#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------
# @ File       : qq.py
# @ Description:  
# @ Author     : Alex Chung
# @ Contact    : yonganzhong@outlook.com
# @ License    : Copyright (c) 2017-2018
# @ Time       : 2020/7/8 下午4:43
# @ Software   : PyCharm
#-------------------------------------------------------

import os
import re
import time
import scrapy
from scrapy.selector import Selector
from selenium import webdriver
from  selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException

from CrawlerAffair.utils import process_title, process_time, process_content, process_label
from CrawlerAffair.items import CrawlerAffairItem
from CrawlerAffair.utils import scroll
from CrawlerAffair.utils import convert_stamp_time

# 无头浏览器设置
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument('--no-sandbox')

driver_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'libs', 'chromedriver')


class QQNewsSpider(scrapy.Spider):
    name = "qq_news_spider"
    urls = ["https://news.qq.com/"]
    allowed_domains = ["qq.com"]
    custom_menu = []
    max_page = 2000

    browser = webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)
    sub_browser = webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)
    detail_browser = webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)

    def start_requests(self):
        # 'http://www.news.cn/local/wgzg.htm'
        urls = self.urls
        for url in urls:
            yield scrapy.Request(url=url, meta=None, callback=self.parse)

    # 整个爬虫结束后关闭浏览器
    def close(self, spider):
        self.browser.quit()
        self.sub_browser.quit()
        self.detail_browser.quit()

    # parse web html
    def parse(self, response):

        self.browser.get(response.url)
        while self.max_page > 0:
            news_element_list = self.browser.find_elements_by_xpath('//ul[@class="list"]/li/div[@class="detail"]/h3/a')
            for news_element in news_element_list:
                url = news_element.get_attribute("href")
                # check is special module
                if len(news_element.find_elements_by_xpath('./span[@class="zt"]')) > 0:
                    yield scrapy.Request(url=url, meta=None, callback=self.parse_special_page)
                else:
                    yield scrapy.Request(url=url, meta=None, callback=self.parse_detail)
                # tail page
            scroll(self.browser)
            self.max_page -= 1
            time.sleep(1)

    def parse_special_page(self, response):
        self.sub_browser.get(response.url)
        time.sleep(5)
        sub_news_element_list = self.sub_browser.find_elements_by_xpath('//div[@class="item-box"]/ul/div/li/div[@class="mod-txt"]/h3/a')
        print(sub_news_element_list)
        for news_element in sub_news_element_list:
            try:
                url = news_element.get_attribute("href")
                # check is special module
                yield scrapy.Request(url=url, meta=None, callback=self.parse_detail)
            except StaleElementReferenceException:
                continue

    def parse_detail(self, response):

        news_item = CrawlerAffairItem()
        spider_time = str(int(time.time()))

        self.detail_browser.get(response.url)
        time.sleep(2)

        publish_time_element = self.detail_browser.find_element_by_xpath('/html/head/meta[contains(@name, "apub:time")]')
        publish_time = publish_time_element.get_attribute("content")
        title_elements = self.detail_browser.find_elements_by_xpath('//div[@class="qq_conent clearfix"]/div[@class="LEFT"]/h1')
        title = [t.text for t in title_elements]

        contents_element = self.detail_browser.find_elements_by_xpath('//div[@class="content-article"]/p')
        contents = [content.text for content in contents_element]
        labels = []

        news_item["spider_time"] = spider_time
        news_item["publish_time"] = process_time(publish_time)
        news_item["title"] = process_title(title)
        news_item["content"] = process_content(contents)
        news_item["label"] = process_label(labels)
        news_item['url'] = response.url.strip()

        return news_item