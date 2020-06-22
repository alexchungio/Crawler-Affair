#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------
# @ File       : china.py
# @ Description:  
# @ Author     : Alex Chung
# @ Contact    : yonganzhong@outlook.com
# @ License    : Copyright (c) 2017-2018
# @ Time       : 2020/6/22 上午11:06
# @ Software   : PyCharm
#-------------------------------------------------------
import time
import scrapy
from selenium import webdriver
from scrapy.selector import Selector
from CrawlerAffair.items import CrawlerAffairItem

class ChinaSpider(scrapy.Spider):
    name = "china_spide"
    allowed_domains = ["china.com.cn"]
    def __init__(self, *args, **kwargs):
        super(ChinaSpider, self).__init__(*args, **kwargs)
        self.start_urls = ['http://news.china.com.cn/']

    # parse web html
    def parse(self, response):
        sel = Selector(response)
        menu_list = sel.xpath('//div[@class="slideNews pr"]/h2/a/@href').extract()
        for menu_url in menu_list:
            # url = menu_url.extract()
            yield scrapy.Request(url=menu_url, meta=None, callback=self.parse_menu_page)


    def parse_menu_page(self, response):
        # response.meta.get("book_item", "")
        sel = Selector(response)
        # get all page
        page_list = [sel.response.url]
        page_list.extend(sel.xpath('//*[@id="autopage"]/center/a/@href').extract())

        for page_url in page_list:

            yield scrapy.Request(url=page_url, meta=None, callback=self.parse_sub_page)

    def parse_sub_page(self, response):

        sel = Selector(response)
        news_list = sel.xpath('//ul[@class="newsList"]/li/a/@href').extract()
        for news_url in news_list:
            news_item = CrawlerAffairItem()
            # label = sel.xpath('//div[@class="v1000 clearfix bc"]/div[@class="fl w650"]/h1[@class="title]/span/text()')
            label = sel.xpath("/html/body/div[2]/div[1]/h1/span/text()").extract()[0]
            news_item['label'] = label.strip()
            yield scrapy.Request(url=news_url, meta={"news_item": news_item}, callback=self.parse_detail)

    def parse_detail(self, response):

        sel = Selector(response)

        news_item = response.meta['news_item']
        spider_time = str(int(time.time()))

        publish_time = sel.xpath('//*[@id="pubtime_baidu"]/text()').extract()[0]

        title = sel.xpath('//h1[@class="articleTitle"]/text()').extract()[0]
        contents = sel.xpath('//*[@id="articleBody"]/p/text()').extract()

        news_item["spider_time"] = spider_time
        news_item["publish_time"] = publish_time.strip()
        news_item["title"] = title.strip()
        news_item["content"] = "\n".join([content.strip() for content in contents])
        news_item['url'] = sel.response.url.strip()

        return news_item




