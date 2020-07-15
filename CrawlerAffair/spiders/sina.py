#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------
# @ File       : sina.py
# @ Description:  
# @ Author     : Alex Chung
# @ Contact    : yonganzhong@outlook.com
# @ License    : Copyright (c) 2017-2018
# @ Time       : 2020/7/8 下午4:41
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


class SinaNewsSpider(scrapy.Spider):
    name = ""
    urls = []
    allowed_domains = ["sina.com.cn"]
    custom_menu = []
    max_page = 2000

    browser = webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)
    detail_browser = webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)

    def start_requests(self):
        # 'http://www.news.cn/local/wgzg.htm'
        urls = self.urls
        for url in urls:
            yield scrapy.Request(url=url, meta=None, callback=self.parse)

    # 整个爬虫结束后关闭浏览器
    def close(self, spider):
        self.browser.quit()
        self.detail_browser.quit()

    # parse web html
    def parse(self, response):

        self.browser.get(response.url)
        while self.max_page > 0:
            news_element_list = self.browser.find_elements_by_xpath('//div[@class="d_list_txt"]/ul/li/span[@class="c_tit"]/a')
            for news_element in news_element_list:
                url = news_element.get_attribute("href")
                # check is special module
                yield scrapy.Request(url=url, meta=None, callback=self.parse_detail)
            scroll(self.detail_browser)
            next_button = self.browser.find_element_by_xpath('//div[@class="pagebox"]/span/a[contains(text(), "下一页")]')
            self.browser.execute_script("arguments[0].click();", next_button)
            time.sleep(2)
            self.max_page -= 1

    def parse_detail(self, response):

        news_item = CrawlerAffairItem()
        spider_time = str(int(time.time()))

        self.detail_browser.get(response.url)
        time.sleep(1)

        publish_time = self.detail_browser.find_element_by_xpath('//div[@id="top_bar"]/div/div[@class="date-source"]/span[@class="date"]').text
        title_elements = self.detail_browser.find_elements_by_xpath('//h1[@class="main-title"]')
        title = [t.text for t in title_elements]
        contents_element = self.detail_browser.find_elements_by_xpath('//div[@id="artibody"]/p')
        contents = [content.text for content in contents_element]
        contents_element_1 = self.detail_browser.find_elements_by_xpath('//div[@ id = "article"]/p')
        contents_1 = [content.text for content in contents_element_1]
        contents.extend(contents_1)
        labels = []

        news_item["spider_time"] = spider_time
        news_item["publish_time"] = process_time(publish_time)
        news_item["title"] = process_title(title)
        news_item["content"] = process_content(contents)
        news_item["label"] = process_label(labels)
        news_item['url'] = response.url.strip()

        return news_item


class SinaSifaCommonSpider(scrapy.Spider):
    name = "sina_sifa_news_spider"
    urls = ["http://sifa.sina.com.cn/news/"]
    allowed_domains = ["sina.com.cn"]
    custom_menu = ["法制热点", "法律法规", "案件聚焦",  "环球法讯"]
    max_page = 200

    browser = webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)
    detail_browser = webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)

    def start_requests(self):
        # 'http://www.news.cn/local/wgzg.htm'
        urls = self.urls
        for url in urls:
            yield scrapy.Request(url=url, meta=None, callback=self.parse)

    # 整个爬虫结束后关闭浏览器
    def close(self, spider):
        self.browser.quit()
        self.detail_browser.quit()

    # parse web html
    def parse(self, response):

        self.browser.get(response.url)
        time.sleep(2)
        while self.max_page > 0:
            menu_button_list = self.browser.find_elements_by_xpath('//div[@id="feedCardConfigurableTabs"]/span')
            for menu_button in menu_button_list:
                if menu_button.text not in self.custom_menu:
                    continue
                else:
                    menu_button.click()

                    while self.max_page > 0:
                        feed_card = self.browser.find_element_by_xpath('//div[@class="feed-card-page"]')
                        while feed_card.get_attribute("style") == "display: none;":
                            scroll(self.browser)

                        news_element_list = self.browser.find_elements_by_xpath('//div[@class="feed-card-item"]/h2/a')
                        for news_element in news_element_list:
                            url = news_element.get_attribute("href")
                            # check is special module
                            yield scrapy.Request(url=url, meta=None, callback=self.parse_detail)
                        next_button_list=self.browser.find_elements_by_xpath('//div[@class="feed-card-page"]/span/a[contains(text(), "下一页")]')
                        if len(next_button_list) == 0:
                            break
                        else:
                            next_button_list[0].click()
                            time.sleep(2)
                        self.max_page -= 1

    def parse_detail(self, response):

        news_item = CrawlerAffairItem()
        spider_time = str(int(time.time()))

        self.detail_browser.get(response.url)
        time.sleep(1)


        publish_time_element_0 = self.detail_browser.find_elements_by_xpath(
            '//div[@id="top_bar"]/div/div[@class="date-source"]/span[@class="date"]')
        publish_time = [content.text for content in publish_time_element_0]
        publish_time_element_1 = self.detail_browser.find_elements_by_xpath(
            '//div[@class="page-info"]/span[@class="time-source"]')
        publish_time_1 = [content.text for content in publish_time_element_1]
        publish_time.extend(publish_time_1)
        publish_time = ''.join(publish_time)

        title_elements_0 = self.detail_browser.find_elements_by_xpath('//h1[@class="main-title"]')
        title = [t.text for t in title_elements_0]
        title_elements_1 = self.detail_browser.find_elements_by_xpath('//div[@class="page-header"]/h1')
        title_1 = [t.text for t in title_elements_1]
        title.extend(title_1)

        contents_element = self.detail_browser.find_elements_by_xpath('//div[@id="artibody"]/p')
        contents = [content.text for content in contents_element]
        contents_element_1 = self.detail_browser.find_elements_by_xpath('//div[@ id = "article"]/p')
        contents_1 = [content.text for content in contents_element_1]
        contents.extend(contents_1)
        labels = []

        news_item["spider_time"] = spider_time
        news_item["publish_time"] = process_time(publish_time)
        news_item["title"] = process_title(title)
        news_item["content"] = process_content(contents)
        news_item["label"] = process_label(labels)
        news_item['url'] = response.url.strip()

        return news_item


class SinaSifaNewsSpider(SinaSifaCommonSpider):
    name = "sina_sifa_news_spider"
    urls = ["http://sifa.sina.com.cn/news/"]
    custom_menu = ["法制热点", "法律法规", "案件聚焦",  "环球法讯"]
    max_page = 200

class SinaSifaPublicitySpider(SinaSifaCommonSpider):
    name = "sina_sifa_publicity_spider"
    urls = ["http://sifa.sina.com.cn/publicity/"]
    custom_menu = ["法院", "司法行政", "检察院"]
    max_page = 200