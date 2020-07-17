#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------
# @ File       : lawlib.py
# @ Description:  
# @ Author     : Alex Chung
# @ Contact    : yonganzhong@outlook.com
# @ License    : Copyright (c) 2017-2018
# @ Time       : 2020/7/13 下午4:46
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

from CrawlerAffair.utils import process_title, process_time, process_content, process_label
from CrawlerAffair.items import CrawlerAffairItem
from CrawlerAffair.utils import scroll



# 无头浏览器设置
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument('--no-sandbox')
# 
driver_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'libs', 'chromedriver')


class LawlibCommonSpider(scrapy.Spider):
    name = ""
    urls = []
    allowed_domains = ["law-lib.com"]
    custom_menu = []

    browser = webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)
    sub_browser = webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)

    def start_requests(self):
        # 'http://www.news.cn/local/wgzg.htm'
        urls = self.urls
        for url in urls:
            yield scrapy.Request(url=url, meta=None, callback=self.parse)

    # 整个爬虫结束后关闭浏览器
    def close(self, spider):
        self.browser.quit()
        self.sub_browser.quit()

    # parse web html
    def parse(self, response):

        # fresh page until successful load page
        while True:
            try:
                # self.browser.get(response.url)
                self.browser.get(response.url)
            except Exception as e:
                time.sleep(2)
                self.browser.refresh()
                break
        # self.browser.manage().timeouts().implicitlyWait(20)
        while True:
            scroll(self.browser, height_ratio=0.6)
            news_element_list = self.browser.find_elements_by_xpath('//ul[@class="line2"]/li/span/a')
            for news_element in news_element_list:
                url = news_element.get_attribute("href")
                yield scrapy.Request(url=url, meta=None, callback=self.parse_detail)
            # tail page
            if len(self.browser.find_elements_by_xpath('//p[@class="p_fenye"]/a[contains(text(), "下一页")]')) == 0:
                break
            else:
                more_button = self.browser.find_element_by_xpath('//p[@class="p_fenye"]/a[contains(text(), "下一页")]')
                self.browser.execute_script("arguments[0].click();", more_button)
                time.sleep(1)



    def parse_detail(self, response):

        news_item = CrawlerAffairItem()
        spider_time = str(int(time.time()))
        self.sub_browser.get(response.url)
        time.sleep(3)

        try:
            publish_time = self.sub_browser.find_element_by_xpath('//div[@class="tit"]/h2/b').text
            title_elements = self.sub_browser.find_elements_by_xpath('//div[@class="tit"]/h3')
            title = [t.text for t in title_elements]

            contents_element = self.sub_browser.find_elements_by_xpath('//div[@class="viewcontent"]')
            contents = [content.text for content in contents_element]
            labels = []
        except Exception as e:
            raise e

        news_item["spider_time"] = spider_time
        news_item["publish_time"] = process_time(publish_time)
        news_item["title"] = process_title(title)
        news_item["content"] = process_content(contents)
        news_item["label"] = process_label(labels)
        news_item['url'] = response.url.strip()

        return news_item


class LawlibXinshiSpider(LawlibCommonSpider):
    name = "lawlib_xinshi_spider"
    urls = ["http://www.law-lib.com/cpws/cpwsml-cx.asp"]


class LawlibMinshiSpider(LawlibCommonSpider):
    name = "lawlib_minshi_spider"
    urls = ["http://www.law-lib.com/cpws/cpwsml-cm.asp"]


class LawlibXinzhenSpider(LawlibCommonSpider):
    name = "lawlib_xinzhen_spider"
    urls = ["http://www.law-lib.com/cpws/cpwsml-cz.asp"]
