#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------
# @ File       : cctv.py
# @ Description:  
# @ Author     : Alex Chung
# @ Contact    : yonganzhong@outlook.com
# @ License    : Copyright (c) 2017-2018
# @ Time       : 2020/7/2 下午4:33
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


class CCTVNewsSpider(scrapy.Spider):
    """
    xin hua general spider
    """
    name = "cctv_news_spider"
    urls = []
    allowed_domains = ["cctv.com"]

    browser = webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)

    def start_requests(self):
        # 'http://www.news.cn/local/wgzg.htm'
        urls = ["http://news.cctv.com/"]
        for url in urls:
            yield scrapy.Request(url=url, meta=None, callback=self.parse)

    # 整个爬虫结束后关闭浏览器
    def close(self, spider):
        self.browser.quit()

    # parse web html
    def parse(self, response):
        sel = Selector(response)


        custom_menu = ["国内", "国际", "社会", "法治",  "文娱", "科技", "生活", "人物"]
        # menu_list = sel.xpath('//div[@class="nav"]/div[@class="wrap"]/a')
        menu_list = sel.xpath('//div[@class="nav_list"]/div[@class="left"]/div/span/a')
        # sub_menu_list = sel.xpath('/html/body/div[7]/div/a')
        for menu_url in menu_list:
            if menu_url.xpath('./text()').extract_first() not in custom_menu:
                continue
            else:
                url = menu_url.xpath('./@href').extract_first()
                self.urls.append(url)
                yield scrapy.Request(url=url, meta=None, callback=self.parse_sub_page, dont_filter=True)

    def parse_sub_page(self, response):

        sel = Selector(response)
        news_list = sel.xpath('//*[@id="newslist"]/li/div[@class="text_con"]/h3/a/@href').extract()
        for news_url in news_list:
            # label = sel.xpath('//div[@class="v1000 clearfix bc"]/div[@class="fl w650"]/h1[@class="title]/span/text()')

            yield scrapy.Request(url=news_url, meta=None, callback=self.parse_detail)

    def parse_detail(self, response):

        sel = Selector(response)

        news_item = CrawlerAffairItem()
        spider_time = str(int(time.time()))
        # '/html/body/div[2]/div[3]/div/div[1]'
        publish_time = sel.xpath('//div[@class="title_area"]/div[@class="info1"]/text()').extract_first()
        title = sel.xpath('//div[@class="title_area"]/h1/text()').extract()
        contents = sel.xpath('//div[@class="content_area"]/p/text()').extract()
        labels = sel.xpath('//ul[@id="searchkeywords"]/li/a/text()').extract()

        news_item["spider_time"] = spider_time
        news_item["publish_time"] = process_time(publish_time)
        news_item["title"] = process_title(title)
        news_item["label"] = process_label(labels)
        news_item["content"] = process_content(contents)
        news_item['url'] = sel.response.url.strip()

        return news_item

class CCTVShipingSpider(scrapy.Spider):
    "央视网观点"
    name = "cctv_shiping_spider"
    urls = []
    allowed_domains = ["cctv.com"]

    browser = webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)

    def start_requests(self):
        # 'http://www.news.cn/local/wgzg.htm'
        urls = ["https://jingji.cctv.com/shiping/index.shtml"]
        for url in urls:
            yield scrapy.Request(url=url, meta=None, callback=self.parse)

    # 整个爬虫结束后关闭浏览器
    def close(self, spider):
        self.browser.quit()

    # parse web html
    def parse(self, response):
        sel = Selector(response)
        # '[contains(text(), ">")]'
        self.browser.get(response.url)
        # 'data-spm-anchor-id="C87458.PehgQlaw4J7u.EbPec9NH7wI8.1225"'
        for i in range(30):
            yield scrapy.Request(url=sel.response.url, meta=None, callback=self.parse_sub_page, dont_filter=True)
            scroll(self.browser)
            next_page = self.browser.find_element_by_xpath('//span[@class="tpb_right"]/a[contains(text(), ">")]')
            self.browser.execute_script("arguments[0].click();", next_page)
            time.sleep(1)

    def parse_sub_page(self, response):

        sel = Selector(response)
        news_list = sel.xpath('//div[@class="img_title_list"]/div/h2/a/@href').extract()
        for news_url in news_list:
            # label = sel.xpath('//div[@class="v1000 clearfix bc"]/div[@class="fl w650"]/h1[@class="title]/span/text()')

            yield scrapy.Request(url=news_url, meta=None, callback=self.parse_detail)

    def parse_detail(self, response):

        sel = Selector(response)

        news_item = CrawlerAffairItem()
        spider_time = str(int(time.time()))
        # '/html/body/div[2]/div[3]/div/div[1]'
        publish_time = sel.xpath('//div[@class="function"]/span[@class="info"]/i/text()').extract()
        title = sel.xpath('//div[@class="cnt_bd"]/h1/text()').extract()
        contents = sel.xpath('//div[@class="cnt_bd"]/p/text()').extract()
        labels = []


        news_item["spider_time"] = spider_time
        news_item["publish_time"] = process_time(publish_time)
        news_item["title"] = process_title(title)
        news_item["label"] = process_label(labels)
        news_item["content"] = process_content(contents)
        news_item['url'] = sel.response.url.strip()

        return news_item

# class XinhuaPoliticsSpider(XinhuaCommonSpider):
#     name = "xinhua_politics_spider"
#     urls = ['http://www.news.cn/politics/index.htm', 'http://www.news.cn/politics/xgc.htm']

class CCTVCaijingSpider(scrapy.Spider):
    "央视网观点"
    name = "cctv_caijing_spider"
    urls = ["https://jingji.cctv.com/caijing/index.shtml"]
    allowed_domains = ["cctv.com"]

    browser = webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)

    def start_requests(self):

        for url in self.urls:
            yield scrapy.Request(url=url, meta=None, callback=self.parse)

    # 整个爬虫结束后关闭浏览器
    def close(self, spider):
        self.browser.quit()

    # parse web html
    def parse(self, response):
        # '[contains(text(), ">")]'
        sel = Selector(response)
        news_list = sel.xpath('//*[@id="leftContent"]/div/h3/span/a/@href').extract()
        for news_url in news_list:
            # label = sel.xpath('//div[@class="v1000 clearfix bc"]/div[@class="fl w650"]/h1[@class="title]/span/text()')

            yield scrapy.Request(url=news_url, meta=None, callback=self.parse_detail)


    def parse_detail(self, response):

        sel = Selector(response)

        news_item = CrawlerAffairItem()
        spider_time = str(int(time.time()))
        # '/html/body/div[2]/div[3]/div/div[1]'
        publish_time = sel.xpath('//div[@class="function"]/span[@class="info"]/i/text()').extract()
        title = sel.xpath('//div[@class="cnt_bd"]/h1/text()').extract()
        contents = sel.xpath('//div[@class="cnt_bd"]/p/text()').extract()
        labels = []

        news_item["spider_time"] = spider_time
        news_item["publish_time"] = process_time(publish_time)
        news_item["title"] = process_title(title)
        news_item["label"] = process_label(labels)
        news_item["content"] = process_content(contents)
        news_item['url'] = sel.response.url.strip()

        return news_item