#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------
# @ File       : thepaper.py
# @ Description:  
# @ Author     : Alex Chung
# @ Contact    : yonganzhong@outlook.com
# @ License    : Copyright (c) 2017-2018
# @ Time       : 2020/7/8 上午11:58
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
from selenium.common.exceptions import ElementNotInteractableException, StaleElementReferenceException

from CrawlerAffair.utils import process_title, process_time, process_content, process_label
from CrawlerAffair.items import CrawlerAffairItem
from CrawlerAffair.utils import scroll


# 无头浏览器设置
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument('--no-sandbox')
# chrome_options.add_argument("window-size=1024,768")

driver_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'libs', 'chromedriver')


class ThepapaperCommonSpider(scrapy.Spider):
    name = ""
    urls = []
    allowed_domains = ["thepaper.cn"]
    max_page = 200
    custom_menu = []

    browser = None

    def start_requests(self):
        # 'http://www.news.cn/local/wgzg.htm'
        urls = self.urls
        for url in urls:
            yield scrapy.Request(url=url, meta=None, callback=self.parse)

    # 整个爬虫结束后关闭浏览器
    def close(self, spider):
        self.browser.quit()

    # parse web html
    def parse(self, response):
        sel = Selector(response)

        self.browser.get(response.url)
        time.sleep(2)
        # show as list
        news_list_button = self.browser.find_element_by_xpath(
            '//div[@id="newsslidebd"]/span[contains(@id, "news_list")]')
        self.browser.execute_script("arguments[0].click();", news_list_button)
        time.sleep(1)
        # scroll to get all page

        while self.max_page > 0:
            try:
                last_height = scroll(self.browser, sleep_time=0.5)
                print(last_height)
                add_buttons = self.browser.find_elements_by_xpath(
                    '//div[@id="addButton"]/a[contains(text(), "点击加载更多")]')
                end_flag = self.browser.find_elements_by_xpath(
                    '//div[@id="addButton"]/em[contains(text(), "已经加载到底部，无法提供更多数据......")]')
                if len(end_flag) > 0:
                    break
                elif len(add_buttons) > 0:
                    self.browser.execute_script("arguments[0].click();", add_buttons[0])
                    time.sleep(1)
                self.max_page -= 1
            except ElementNotInteractableException:
                break
            except StaleElementReferenceException:
                break
        time.sleep(1)
        news_element_list = self.browser.find_elements_by_xpath(
            '//div[@id="listContent"]/div[@class="news_li"]/h2/a')
        news_list = [news.get_attribute("href") for news in news_element_list]
        for news_url in news_list:
            # label = sel.xpath('//div[@class="v1000 clearfix bc"]/div[@class="fl w650"]/h1[@class="title]/span/text()')
            yield scrapy.Request(url=news_url, meta=None, callback=self.parse_detail)

    def parse_detail(self, response):

        sel = Selector(response)

        news_item = CrawlerAffairItem()
        spider_time = str(int(time.time()))
        # '/html/body/div[2]/div[3]/div/div[1]'
        '/html/body/div[3]/div[1]/div[1]/h1'
        publish_time = sel.xpath('//div[@class="newscontent"]/div[@class="news_about"]/p/text()').extract()
        title = sel.xpath('//div[@class="newscontent"]/h1/text()').extract()
        contents = sel.xpath('//div[@class="news_txt"]/text()').extract()
        labels = []
        if len(sel.xpath('//div[@class="news_keyword"]/text()').extract()) > 0:
            labels = sel.xpath('//div[@class="news_keyword"]/text()').extract_first().split('>>')[-1].split(',')

        news_item["spider_time"] = spider_time
        news_item["publish_time"] = process_time(publish_time)
        news_item["title"] = process_title(title)
        news_item["label"] = process_label(labels)
        news_item["content"] = process_content(contents)
        news_item['url'] = sel.response.url.strip()

        return news_item


class ThepaperSelectSpider(ThepapaperCommonSpider):
    name = "thepaper_select_spider"
    urls = ["https://www.thepaper.cn/"]
    allowed_domains = ["thepaper.cn"]
    max_page = 100
    webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)

class ThepaperShishiSpider(ThepapaperCommonSpider):
    name = "thepaper_shishi_spider"
    urls = ["https://www.thepaper.cn/channel_25950"]
    allowed_domains = ["thepaper.cn"]
    max_page = 100
    webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)