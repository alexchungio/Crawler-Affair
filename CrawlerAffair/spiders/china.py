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
import re
from scrapy.selector import Selector

from CrawlerAffair.utils import process_title, process_time, process_content, process_label
from CrawlerAffair.items import CrawlerAffairItem


class ChinaNewsSpider(scrapy.Spider):
    name = "china_news_spider"
    allowed_domains = ["china.com.cn"]
    # def __init__(self, *args, **kwargs):
    #     super(ChinaSpider, self).__init__(*args, **kwargs)
        # self.start_urls = ['http://news.china.com.cn/']

    def start_requests(self):
        urls = ['http://news.china.com.cn/']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

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
            # news_item = CrawlerAffairItem()
            # label = sel.xpath('//div[@class="v1000 clearfix bc"]/div[@class="fl w650"]/h1[@class="title]/span/text()')
            # label = sel.xpath("/html/body/div[2]/div[1]/h1/span/text()").extract()[0]
            # news_item['label'] = label.strip()
            yield scrapy.Request(url=news_url, meta=None, callback=self.parse_detail)

    def parse_detail(self, response):

        sel = Selector(response)

        news_item = CrawlerAffairItem()
        spider_time = str(int(time.time()))

        publish_time = sel.xpath('//*[@id="pubtime_baidu"]/text()').extract()
        if len(publish_time) > 0:
            publish_time = publish_time[0]
        else:
            publish_time = None

        title = sel.xpath('//h1[@class="articleTitle"]/text()').extract()
        contents = sel.xpath('//*[@id="articleBody"]/p/text()').extract()
        labels = sel.xpath('//*[@id="articleKeywords"]/a/text()').extract()

        news_item["spider_time"] = spider_time
        news_item["publish_time"] = process_time(publish_time.strip())
        news_item["title"] = process_title(title)
        news_item['label'] = process_label(labels)
        news_item["content"] = process_content(contents)
        news_item['url'] = sel.response.url.strip()

        return news_item


class ChinaAffairSpider(scrapy.Spider):
    name = "china_affair_spider"
    allowed_domains = ["china.com.cn"]

    def start_requests(self):
        urls = ['http://zw.china.com.cn/']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    # parse web html
    def parse(self, response):
        sel = Selector(response)
        # menu_list = sel.xpath('//div[@class="nav"]/div[@class="wrap"]/a')
        iframe_url = sel.xpath('/html/body/div[1]/iframe').extract_first()

        regex = re.compile("http://[^\s]*.htm")
        url = regex.findall(iframe_url)[0]

        yield scrapy.Request(url=url, meta=None, callback=self.parse_iframe)


    def parse_iframe(self, response):

        sel = Selector(response)
        custom_menu = ["政务要闻", "政务信息", "地方政务", "政务信息"]
        menu_list = sel.xpath('//div[@class="nav"]/div[@class="wrap"]/a')
        for menu_url in menu_list:
            if menu_url.xpath('./text()').extract_first() not in custom_menu:
                continue
            else:
                url = menu_url.xpath('./@href').extract_first()
                yield scrapy.Request(url=url, meta=None, callback=self.parse_menu_page)

    def parse_menu_page(self, response):

        sel = Selector(response)
        page_list = [sel.response.url]
        page_list.extend(sel.xpath('//*[@id="autopage"]/center/a/@href').extract())
        for page_url in page_list:
            yield scrapy.Request(url=page_url, meta=None, callback=self.parse_sub_page)

    def parse_sub_page(self, response):

        sel = Selector(response)

        news_list = sel.xpath('//ul/li/a/@href').extract()
        for news_url in news_list:
            # label = sel.xpath('//div[@class="v1000 clearfix bc"]/div[@class="fl w650"]/h1[@class="title]/span/text()')
            yield scrapy.Request(url=news_url, meta=None, callback=self.parse_detail)

    def parse_detail(self, response):

        sel = Selector(response)

        news_item = CrawlerAffairItem()
        spider_time = str(int(time.time()))

        publish_time = sel.xpath('//div[@class="big_img"]/div[@class="more"]/text()')
        if len(publish_time) > 0:
            publish_time = publish_time[0]
        else:
            publish_time = None

        title = sel.xpath('//div[@class="big_img"]/h1/text()').extract()
        contents = sel.xpath('//*[@id="content"]/p/text()').extract()
        labels = []

        news_item["spider_time"] = spider_time
        news_item["publish_time"] = process_time(publish_time)
        news_item["title"] = process_title(title)
        news_item["label"] = process_label(labels)
        news_item["content"] = process_content(contents)
        news_item['url'] = sel.response.url.strip()

        return news_item


class ChinaOpinionSpider(scrapy.Spider):
    name = "china_opinion_spider"
    allowed_domains = ["china.com.cn"]

    def start_requests(self):
        urls = ['http://opinion.china.com.cn/']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    # parse web html
    def parse(self, response):
        sel = Selector(response)
        custom_menu = ["观点", "专栏", "图说"]

        # menu_list = sel.xpath('//div[@class="nav"]/div[@class="wrap"]/a')
        menu_list = sel.xpath('//div[@class="opinion-nav"]/div/ul/li/a')

        for menu_url in menu_list:
            if menu_url.xpath('./text()').extract_first() not in custom_menu:
                continue
            else:
                url = menu_url.xpath('./@href').extract_first()
                url = sel.response.urljoin(url)
                yield scrapy.Request(url=url, meta=None, callback=self.parse_menu_page)

    def parse_menu_page(self, response):

        sel = Selector(response)

        num_page = int(sel.xpath('//div[@class="list-page clearfix"]/span/text()').extract_first().split('/')[-1])
        for i in range(1, num_page+1):
            page_url = re.sub('\d', str(i), sel.response.url)
            yield scrapy.Request(url=page_url, meta=None, callback=self.parse_sub_page)

    def parse_sub_page(self, response):

        sel = Selector(response)

        news_list = sel.xpath('//ul[@class="opinion-list-2 pt50"]/li/dl/dd/h5/a/@href').extract()
        for news_url in news_list:
            try:
                yield scrapy.Request(url=news_url, meta=None, callback=self.parse_detail)
            except Exception as e:
                continue

    def parse_detail(self, response):

        sel = Selector(response)

        news_item = CrawlerAffairItem()
        spider_time = str(int(time.time()))

        publish_time = sel.xpath('//div[@class="article-info"]/p/span[@class="article-timestamp ml10"]/text()')
        if len(publish_time) > 0:
            publish_time = publish_time[0]
        else:
            publish_time = None

        title = sel.xpath('//div[@class="article-title"]/h1/text()').extract()
        contents = sel.xpath('//div[@class="article-content"]/p/text()').extract()
        labels = sel.xpath('//div[@class="fl ml10 article-tags"]/a/text()').extract()

        news_item["spider_time"] = spider_time
        news_item["publish_time"] = process_time(publish_time)
        news_item["title"] = process_title(title)
        news_item["label"] = process_label(labels)
        news_item["content"] = process_content(contents)
        news_item['url'] = sel.response.url.strip()

        return news_item


class ChinaTheorySpider(scrapy.Spider):
    name = "china_theory_spider"
    allowed_domains = ["china.com.cn"]

    def start_requests(self):
        urls = ['http://www.china.com.cn/opinion/theory/']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    # parse web html
    def parse(self, response):
        sel = Selector(response)
        # menu_list = sel.xpath('//div[@class="nav"]/div[@class="wrap"]/a')
        iframe_url = sel.xpath('//*[@id="cTop"]').extract_first()

        regex = re.compile("http://[^\s]*.htm")
        url = regex.findall(iframe_url)[0]

        yield scrapy.Request(url=url, meta={"base_url": sel.response.url}, callback=self.parse_iframe)

    def parse_iframe(self, response):

        sel = Selector(response)
        base_url = sel.response.meta["base_url"]
        custom_menu = ["理论热点", "高层声音", "媒体社论"]
        menu_list = sel.xpath('//div[@class="nav"]/ul/li/a')
        for menu_url in menu_list:
            if menu_url.xpath('./text()').extract_first() not in custom_menu:
                continue
            else:
                url = menu_url.xpath('./@href').extract_first()
                url = base_url + url
                yield scrapy.Request(url=url, meta=None, callback=self.parse_menu_page)

    def parse_menu_page(self, response):

        sel = Selector(response)
        page_list = [sel.response.url]
        page_list.extend(sel.xpath('//div[@class="leftbox"]/div/center/a/@href').extract())
        for page_url in page_list:
            yield scrapy.Request(url=page_url, meta=None, callback=self.parse_sub_page)

    def parse_sub_page(self, response):

        sel = Selector(response)

        news_list = sel.xpath('//div[@class="leftbox"]/ul/li/a/@href').extract()
        for news_url in news_list:
            # label = sel.xpath('//div[@class="v1000 clearfix bc"]/div[@class="fl w650"]/h1[@class="title]/span/text()')
            yield scrapy.Request(url=news_url, meta=None, callback=self.parse_detail)

    def parse_detail(self, response):

        sel = Selector(response)

        news_item = CrawlerAffairItem()
        spider_time = str(int(time.time()))

        publish_time = sel.xpath('//div[@class="info"]/div[@class="pub_date"]/*[@id="pubtime_baidu"]/text()')
        if len(publish_time) > 0:
            publish_time = publish_time[0]
        else:
            publish_time = None

        title = sel.xpath('//div[@class="leftbox"]/h1[@class="artTitle"]/text()').extract()
        contents = sel.xpath('//div[@class="info"]/div[@id="artbody"]/p/text()').extract()
        labels = []

        news_item["spider_time"] = spider_time
        news_item["publish_time"] = process_time(publish_time)
        news_item["title"] = process_title(title)
        news_item["label"] = process_label(labels)
        news_item["content"] = process_content(contents)
        news_item['url'] = sel.response.url.strip()

        return news_item


if __name__ == "__main__":
    local_time = "1970-01-01 08:00:00"

