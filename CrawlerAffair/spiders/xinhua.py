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
from selenium.webdriver.common.action_chains import ActionChains

from CrawlerAffair.utils import process_title, process_time, process_content, process_label
from CrawlerAffair.items import CrawlerAffairItem


# 无头浏览器设置
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument('--no-sandbox')

driver_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'libs', 'chromedriver')


class XinhuaCommonSpider(scrapy.Spider):
    """
    xin hua general spider
    """
    name = ""
    urls = []
    allowed_domains = ["news.cn", "xinhuanet.com"]

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
        # sel = Selector(response)

        # custom_menu = ["地方首页", "微观中国"]
        # # menu_list = sel.xpath('//div[@class="nav"]/div[@class="wrap"]/a')
        # menu_list = sel.xpath('//div[@class="nav domPC"]/div[@class="widthMain"]/a')
        # # sub_menu_list = sel.xpath('/html/body/div[7]/div/a')
        # for menu_url in menu_list:
        #     if menu_url.xpath('./text()').extract_first() not in custom_menu:
        #         continue
        #     else:
        #         sub_url = menu_url.xpath('./@href').extract_first()
        #         url = sel.response.urljoin(sub_url)
        #         yield scrapy.Request(url=url, meta=None, callback=self.parse_sub_page, dont_filter=True)
        sel = Selector(response)
        news_list = sel.xpath('//ul[@class="dataList"]/li/h3/a/@href').extract()
        for news_url in news_list:
            # label = sel.xpath('//div[@class="v1000 clearfix bc"]/div[@class="fl w650"]/h1[@class="title]/span/text()')
            yield scrapy.Request(url=news_url, meta=None, callback=self.parse_detail)

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
        # '/html/body/div[2]/div[3]/div/div[1]'
        publish_time = sel.xpath('//div[@class="h-news"]/div[@class="h-info"]/span/text()').extract_first()
        title = sel.xpath('//div[@class="h-news"]/div[@class="h-title"]/text()').extract()
        contents = sel.xpath('//div[@id="p-detail"]/p/text()').extract()
        labels = []

        news_item["spider_time"] = spider_time
        news_item["publish_time"] = process_time(publish_time)
        news_item["title"] = process_title(title)
        news_item["label"] = process_label(labels)
        news_item["content"] = process_content(contents)
        news_item['url'] = sel.response.url.strip()

        return news_item


class XinhuaPoliticsSpider(XinhuaCommonSpider):
    name = "xinhua_politics_spider"
    urls = ['http://www.news.cn/politics/index.htm', 'http://www.news.cn/politics/xgc.htm']


class XinhuaLocalSpider(XinhuaCommonSpider):

    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
    name = "xinhua_local_spider"
    urls = ['http://www.news.cn/local/index.htm', 'http://www.news.cn/local/wgzg.htm']

    webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)

class XinhualegalSpider(XinhuaCommonSpider):
    name = "xinhua_legal_spider"
    urls = ["http://www.news.cn/legal/index.htm", "http://www.news.cn/legal/fy.htm", "http://www.news.cn/legal/ffu.htm"]
    webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)

class XinhuaRenshiSpider(XinhuaCommonSpider):
    name= "xinhua_renshi_spider"
    urls = ["http://www.xinhuanet.com/politics/rs.htm"]
    webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)

class XinhuaInfoSpider(XinhuaCommonSpider):
    name = "xinhua_info_spider"
    # urls = ["http://www.news.cn/info/index.htm", "http://www.news.cn/info/tx.htm", "http://www.news.cn/info/ydhlw.htm"]
    urls = ["http://www.news.cn/info/index.htm"]
    allowed_domains = ["news.cn", "xinhuanet.com"]

    browser = webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)

    def start_requests(self):
        # 'http://www.news.cn/local/wgzg.htm'
        for index in range(1, 5):
            self.index = index
            # ActionChains(browser).move_to_element(menu_switch).perform()
            yield scrapy.Request(url=self.urls[0], meta=None, callback=self.parse, dont_filter=True)


class XinhuaSilkRoad(XinhuaCommonSpider):
    name = "xinhua_siklroad_spider"
    # urls = ["http://www.news.cn/info/index.htm", "http://www.news.cn/info/tx.htm", "http://www.news.cn/info/ydhlw.htm"]
    urls = []
    webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)

    def start_requests(self):
        urls = ["http://www.news.cn/silkroad/index.htm"]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    # parse web html
    def parse(self, response):
        sel = Selector(response)

        custom_menu = ["丝路聚焦", "中国议程", "深度透视", "丝路智库", "丝路商机", "丝路国际", "丝路中国", "丝路旅游"]
        # menu_list = sel.xpath('//div[@class="nav"]/div[@class="wrap"]/a')
        menu_list = sel.xpath('//div[@class="silkroad-nav"]/ul/li/a')
        # sub_menu_list = sel.xpath('/html/body/div[7]/div/a')
        for menu_url in menu_list:
            if menu_url.xpath('./text()').extract_first() not in custom_menu:
                continue
            else:
                sub_url = menu_url.xpath('./@href').extract_first()
                url = sel.response.urljoin(sub_url)
                self.urls.append(url)
                yield scrapy.Request(url=url, meta=None, callback=self.parse_sub_page)

    def parse_sub_page(self, response):

        sel = Selector(response)
        news_list = sel.xpath('//ul[@id="showData0"]/li/h3/a/@href').extract()
        for news_url in news_list:
            # label = sel.xpath('//div[@class="v1000 clearfix bc"]/div[@class="fl w650"]/h1[@class="title]/span/text()')
            yield scrapy.Request(url=news_url, meta=None, callback=self.parse_detail)




# 爬不到数据
# 前后域名发生变化， 导致爬取页面的域名没有包含在all_domain 中，从而导致页面爬取失败
# 解决： 将字页面域名手动添加到allow_domain 中


# 调用两次url, 获取失败
# no more duplicates will be shown (see DUPEFILTER_DEBUG to show all duplicates
# scrapy.Request 中的dont_filter 会自动过滤重复页面， 默认值为dont_filter=false, 因此会执行过滤操作
# 解决：为了进行两次爬取，设置dont_filter=True

# 每次点击事件之后必须控制延时，否则会由于页面无法及晒刷新而导致
