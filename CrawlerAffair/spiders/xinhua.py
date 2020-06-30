#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------
# @ File       : xinhua.py
# @ Description:  
# @ Author     : Alex Chung
# @ Contact    : yonganzhong@outlook.com
# @ License    : Copyright (c) 2017-2018
# @ Time       : 2020/6/28 下午5:50
# @ Software   : PyCharm
#-------------------------------------------------------

import os
import re
import time
import scrapy
from scrapy.selector import Selector
from selenium import webdriver
from  selenium.webdriver.chrome.options import Options

from CrawlerAffair.utils import process_title, process_time, process_content, process_label
from CrawlerAffair.items import CrawlerAffairItem

# 无头浏览器设置
chorme_options = Options()
# chorme_options.add_argument("--headless")
chorme_options.add_argument("--disable-gpu")
# chrome_options.add_argument('--no-sandbox')

driver_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'libs', 'chromedriver')

class XinhuaPoliticsSpider(scrapy.Spider):
    name = "xinhua_politics_spider"
    allowed_domains = ["news.cn", "xinhuanet.com"]


    browser = webdriver.Chrome(executable_path=driver_path, chrome_options=chorme_options)

    def start_requests(self):
        urls = ['http://www.news.cn/politics/']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    # 整个爬虫结束后关闭浏览器
    def close(self, spider):
        self.browser.quit()

    # parse web html
    def parse(self, response):
        sel = Selector(response)

        custom_menu = ["时政首页"]
        # menu_list = sel.xpath('//div[@class="nav"]/div[@class="wrap"]/a')
        menu_list = sel.xpath('//div[@class="nav domPC"]/div[@class="widthMain"]/a')
        # sub_menu_list = sel.xpath('/html/body/div[7]/div/a')
        for menu_url in menu_list:
            if menu_url.xpath('./text()').extract_first() not in custom_menu:
                continue
            else:
                sub_url = menu_url.xpath('./@href').extract_first()
                url = sel.response.urljoin(sub_url)
                yield scrapy.Request(url=url, meta=None, callback=self.parse_sub_page)

    def parse_sub_page(self, response):

        sel = Selector(response)
        news_list = sel.xpath('//ul[@class="dataList"]/li/h3/a/@href').extract()
        for news_url in news_list:
            # label = sel.xpath('//div[@class="v1000 clearfix bc"]/div[@class="fl w650"]/h1[@class="title]/span/text()')
            yield scrapy.Request(url=news_url, meta=None, callback=self.parse_detail)

    def parse_detail(self, response):

        sel = Selector(response)

        news_item = CrawlerAffairItem()
        spider_time = str(int(time.time()))

        publish_time = sel.xpath('//div[@class="h-news"]/div[@class="h-info"]/span/text()').extract_first()
        title = sel.xpath('//div[@class="h-news"]/div[class="h-title"]/text()').extract()
        contents = sel.xpath('//div[@id="p-detail"]/p/text()').extract()
        labels = []

        news_item["spider_time"] = spider_time
        news_item["publish_time"] = process_time(publish_time)
        news_item["title"] = process_title(title)
        news_item["label"] = process_label(labels)
        news_item["content"] = process_content(contents)
        news_item['url'] = sel.response.url.strip()


        return news_item



# 爬不到数据
# 前后域名发生变化， 导致爬取页面的域名没有包含在all_domain 中
