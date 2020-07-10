#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------
# @ File       : chinadaily.py
# @ Description:  
# @ Author     : Alex Chung
# @ Contact    : yonganzhong@outlook.com
# @ License    : Copyright (c) 2017-2018
# @ Time       : 2020/7/7 下午5:52
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

driver_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'libs', 'chromedriver')


class ChinadailyCommonSpider(scrapy.Spider):
    name = "chinadaily_china_spider"
    urls = ["https://china.chinadaily.com.cn"]
    allowed_domains = ["chinadaily.com.cn"]
    custom_menu = []

    browser = webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)

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

        menu_list = sel.xpath('//div[@class="jr-link2"]/ul/li/a')
        # 'data-spm-anchor-id="C87458.PehgQlaw4J7u.EbPec9NH7wI8.1225"'
        for menu_url in menu_list:
            if menu_url.xpath('./text()').extract_first() not in self.custom_menu:
                continue
            else:
                url = 'https:' + menu_url.xpath('./@href').extract_first()
                yield scrapy.Request(url=url, meta=None, callback=self.parse_menu_page)

    def parse_menu_page(self, response):

        sel = Selector(response)
        self.browser.get(response.url)
        time.sleep(1)
        # 'data-spm-anchor-id="C87458.PehgQlaw4J7u.EbPec9NH7wI8.1225"'
        for i in range(40):
            news_element_list = self.browser.find_elements_by_xpath(
                '//div[@class="left-liebiao"]/div[@class="busBox3"]/div/div/h3/a')
            news_list = [news.get_attribute("href") for news in news_element_list]
            yield scrapy.Request(url=sel.response.url, meta={"news_list": news_list}, callback=self.parse_sub_page,
                                 dont_filter=True)
            scroll(self.browser)
            next_page = self.browser.find_element_by_xpath('//div[@id="div_currpage"]/a[contains(text(), "下一页")]')
            self.browser.execute_script("arguments[0].click();", next_page)
            time.sleep(1)

    def parse_sub_page(self, response):

        news_list = response.meta["news_list"]
        for news_url in news_list:
            # label = sel.xpath('//div[@class="v1000 clearfix bc"]/div[@class="fl w650"]/h1[@class="title]/span/text()')
            yield scrapy.Request(url=news_url, meta=None, callback=self.parse_detail)

    def parse_detail(self, response):

        sel = Selector(response)

        news_item = CrawlerAffairItem()
        spider_time = str(int(time.time()))
        # '/html/body/div[2]/div[3]/div/div[1]'
        publish_time = sel.xpath('//div[@class="fenx"]/div[@class="xinf-le"]/text()').extract()
        title = sel.xpath('//div[@class="container-left2"]/h1/text()').extract()
        contents = sel.xpath('//div[@id="Content"]/p/text()').extract()
        labels = []

        news_item["spider_time"] = spider_time
        news_item["publish_time"] = process_time(publish_time)
        news_item["title"] = process_title(title)
        news_item["label"] = process_label(labels)
        news_item["content"] = process_content(contents)
        news_item['url'] = sel.response.url.strip()

        return news_item


class ChinadailyWorldSpider(ChinadailyCommonSpider):
    name = "chinadaily_world_spider"
    urls = ["https://china.chinadaily.com.cn"]
    custom_menu = ["独家", "要闻", "滚动"]


class ChinadailyChinaSpider(ChinadailyCommonSpider):
    name = "chinadaily_china_spider"
    urls = ["https://china.chinadaily.com.cn"]
    custom_menu = ["要闻", "独家"]
