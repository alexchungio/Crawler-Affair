#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------
# @ File       : renmin.py
# @ Description:  
# @ Author     : Alex Chung
# @ Contact    : yonganzhong@outlook.com
# @ License    : Copyright (c) 2017-2018
# @ Time       : 2020/6/22 上午10:35
# @ Software   : PyCharm
#-------------------------------------------------------
import re
import time
import scrapy
from scrapy.selector import Selector

from CrawlerAffair.utils import process_title, process_time, process_content, process_label
from CrawlerAffair.items import CrawlerAffairItem


class RenminPoliticsSpider(scrapy.Spider):
    name = "renmin_politics_spider"
    allowed_domains = ["people.com.cn"]

    def start_requests(self):
        urls = ['http://politics.people.com.cn/']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    # parse web html
    def parse(self, response):
        sel = Selector(response)
        custom_menu = ["本网原创", "高层动态", "中央部委", "反腐倡廉", "时事解读"]
        # menu_list = sel.xpath('//div[@class="nav"]/div[@class="wrap"]/a')
        menu_list = sel.xpath('//div[@class="pd_nav w1000 white mt15"]/a')
        for menu_url in menu_list:
            if menu_url.xpath('./text()').extract_first() not in custom_menu:
                continue
            else:

                url = menu_url.xpath('./@href').extract_first()
                print(url)
                yield scrapy.Request(url=url, meta=None, callback=self.parse_menu_page)

    def parse_menu_page(self, response):

        sel = Selector(response)
        base_url = '/'.join(sel.response.url.split('/')[:-1])
        page_list = [sel.response.url]
        sub_list = sel.xpath('//*[@class="page_n clearfix"]/a/@href').extract()[:-1]
        page_list.extend([base_url+'/'+url for url in sub_list])
        for page_url in page_list:
            yield scrapy.Request(url=page_url, meta=None, callback=self.parse_sub_page)

    def parse_sub_page(self, response):

        sel = Selector(response)
        base_url = '/'.join(sel.response.url.split('/')[:-3])
        sub_news_list = sel.xpath('//div[@class="ej_list_box clear"]/ul/li/a/@href').extract()
        news_list = [base_url+'/'+url for url in sub_news_list]
        for news_url in news_list:
            # label = sel.xpath('//div[@class="v1000 clearfix bc"]/div[@class="fl w650"]/h1[@class="title]/span/text()')
            yield scrapy.Request(url=news_url, meta=None, callback=self.parse_detail)

    def parse_detail(self, response):

        sel = Selector(response)

        news_item = CrawlerAffairItem()
        spider_time = str(int(time.time()))


        publish_time = sel.xpath('//div[@class ="box01"]/div[@class="fl"]/text()').extract_first()
        title = sel.xpath('//div[@class="clearfix w1000_320 text_title"]/h1/text()').extract()
        contents = sel.xpath('//*[@id="rwb_zw"]/p/text()').extract()
        labels = []

        news_item["spider_time"] = spider_time
        news_item["publish_time"] = process_time(publish_time)
        news_item["title"] = process_title(title)
        news_item["label"] = process_label(labels)
        news_item["content"] = process_content(contents)
        news_item['url'] = sel.response.url.strip()

        return news_item



if __name__ == "__main__":
    pass