#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------
# @ File       : gov.py
# @ Description:  
# @ Author     : Alex Chung
# @ Contact    : yonganzhong@outlook.com
# @ License    : Copyright (c) 2017-2018
# @ Time       : 2020/7/8 下午7:03
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
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument('--no-sandbox')

driver_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'libs', 'chromedriver')


class GovOnePageSpider(scrapy.Spider):
    name = ""
    urls = []
    allowed_domains = ["gov.cn"]
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

        self.browser.get(response.url)
        pre_all_window = self.browser.window_handles
        scroll(self.browser)
        more_button = self.browser.find_element_by_xpath('//span[@class="public_more"]/a')
        self.browser.execute_script("arguments[0].click();", more_button)
        time.sleep(1)
        # menu_url_list = [menu_button.get_attribute("href") for menu_button in menu_button_list]


        # 针对弹出页面后无法获取当前页面进行处理（非原页面刷新）
        current_all_window = self.browser.window_handles
        for window in current_all_window:
            if window not in pre_all_window:
                self.browser.switch_to.window(window)
        scroll(self.browser)

        num_page = self.browser.find_element_by_xpath('//*[@id="toPage"]/li[starts-with(text(), "共")]').text
        num_page = int(re.findall(r'\d+', num_page)[0])
        # get page news list
        for index in range(num_page):
            url = re.sub('\d+.htm', f'{index}.htm', self.browser.current_url)
            yield scrapy.Request(url=url, meta=None, callback=self.parse_sub_page, dont_filter=True)


    def parse_sub_page(self, response):

        sel = Selector(response)

        # time.sleep(1)
        news_list = sel.xpath('//*[@class="listTxt"]/li/h4/a/@href').extract()
        for news_url in news_list:
            # label = sel.xpath('//div[@class="v1000 clearfix bc"]/div[@class="fl w650"]/h1[@class="title]/span/text()')
            yield scrapy.Request(url=news_url, meta=None, callback=self.parse_detail)

    def parse_detail(self, response):

        sel = Selector(response)
        news_item = CrawlerAffairItem()
        spider_time = str(int(time.time()))

        publish_time = sel.xpath('//div[@class="pages-date"]/text()').extract_first()
        # process title
        title = []
        title_0 = sel.xpath('//div[@class="article oneColumn pub_border"]/h1/text()').extract()
        title_1 = sel.xpath('//div[@class="pages-title"]/text()').extract()
        if len(title_0) > 0:
            title = title_0
        elif len(title_1) > 0:
            title = title_1

        contents = sel.xpath('//div[@class="pages_content"]/p/text()').extract()
        contents_1 = sel.xpath('//*[@id="UCAP-CONTENT"]/p/span/span/text()').extract()
        contents.extend(contents_1)
        contents_2= sel.xpath('//div[@class="pages_content"]/p/span/text()').extract()
        contents.extend(contents_2)
        print(contents)

        labels = []
        news_item["spider_time"] = spider_time
        news_item["publish_time"] = process_time(publish_time)
        news_item["title"] = process_title(title)
        news_item["label"] = process_label(labels)
        news_item["content"] = process_content(contents)
        news_item['url'] = response.url.strip()

        return news_item


class GovMultiPageSpider(scrapy.Spider):
    name = ""
    urls = []
    allowed_domains = ["gov.cn"]
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

        self.browser.get(response.url)
        all_menu_list = self.browser.find_elements_by_xpath('//div[@class="pannel-title tit_s01"]')

        for menu_element in all_menu_list:
            if menu_element.find_element_by_xpath('./div[@class="title-inner"]/span/a').text not in self.custom_menu:
                continue
            else:
                more_menu = menu_element.find_element_by_xpath('./span[@class="more"]/a')

            main_window = self.browser.current_window_handle

            pre_all_window = self.browser.window_handles
            self.browser.execute_script("arguments[0].click();", more_menu)
            time.sleep(1)
            # menu_url_list = [menu_button.get_attribute("href") for menu_button in menu_button_list]
            # 针对弹出页面后无法获取当前页面进行处理（非原页面刷新）
            current_all_window = self.browser.window_handles
            for window in current_all_window:
                if window not in pre_all_window:
                    self.browser.switch_to.window(window)

            yield scrapy.Request(url=self.browser.current_url, meta=None, callback=self.parse_sub_menu, dont_filter=True)

            self.browser.switch_to_window(main_window)

    def parse_sub_menu(self, response):

        self.sub_browser.get(response.url)
        scroll(self.sub_browser)
        more_button = self.sub_browser.find_element_by_xpath('//span[@class="public_more"]/a')
        pre_all_window = self.sub_browser.window_handles
        self.sub_browser.execute_script("arguments[0].click();", more_button)
        current_all_window = self.sub_browser.window_handles
        for window in current_all_window:
            if window not in pre_all_window:
                self.sub_browser.switch_to.window(window)
        scroll(self.sub_browser)

        num_page = self.sub_browser.find_element_by_xpath('//*[@id="toPage"]/li[starts-with(text(), "共")]').text
        num_page = int(re.findall(r'\d+', num_page)[0])
        # get page news list
        for index in range(num_page):
            url = re.sub('\d+.htm', f'{index}.htm', self.sub_browser.current_url)
            yield scrapy.Request(url=url, meta=None, callback=self.parse_sub_page, dont_filter=True)

    def parse_sub_page(self, response):

        sel = Selector(response)

        # time.sleep(1)
        news_list = sel.xpath('//*[@class="listTxt"]/li/h4/a/@href').extract()
        for news_url in news_list:
            # label = sel.xpath('//div[@class="v1000 clearfix bc"]/div[@class="fl w650"]/h1[@class="title]/span/text()')
            yield scrapy.Request(url=news_url, meta=None, callback=self.parse_detail)

    def parse_detail(self, response):

        sel = Selector(response)
        news_item = CrawlerAffairItem()
        spider_time = str(int(time.time()))

        publish_time = sel.xpath('//div[@class="pages-date"]/text()').extract_first()
        # process title
        title = []
        title_0 = sel.xpath('//div[@class="article oneColumn pub_border"]/h1/text()').extract()
        title_1 = sel.xpath('//div[@class="pages-title"]/text()').extract()
        if len(title_0) > 0:
            title = title_0
        elif len(title_1) > 0:
            title = title_1

        contents = sel.xpath('//div[@class="pages_content"]/p/text()').extract()
        contents_1 = sel.xpath('//*[@id="UCAP-CONTENT"]/p/span/span/text()').extract()
        contents.extend(contents_1)
        contents_2= sel.xpath('//div[@class="pages_content"]/p/span/text()').extract()
        contents.extend(contents_2)
        print(contents)

        labels = []
        news_item["spider_time"] = spider_time
        news_item["publish_time"] = process_time(publish_time)
        news_item["title"] = process_title(title)
        news_item["label"] = process_label(labels)
        news_item["content"] = process_content(contents)
        news_item['url'] = response.url.strip()

        return news_item


class GovYaowenSpider(GovOnePageSpider):
    name = "gov_yaowen_spider"
    urls = ["http://www.gov.cn/xinwen/yaowen.htm"]


class GovPolicySpider(GovOnePageSpider):
    name = "gov_policy_spider"
    urls = ["http://www.gov.cn/zhengce/zuixin.htm"]


class GovLianboSpider(GovMultiPageSpider):
    name = "gov_lianbo_spider"
    urls = ["http://www.gov.cn/xinwen/lianbo/index.htm"]
    allowed_domains = ["gov.cn"]
    custom_menu = ["部门","地方"]

class GovFabuSpider(GovMultiPageSpider):
    name = "gov_fabu_spider"
    urls = ["http://www.gov.cn/xinwen/fabu/index.htm"]
    allowed_domains = ["gov.cn"]
    custom_menu = ["部门","其他"]

class GovRenmianSpider(scrapy.Spider):
    name = "gov_renmian_spider"
    urls = ["http://www.gov.cn/xinwen/renmian/index.htm"]
    allowed_domains = ["gov.cn"]
    custom_menu= ["中央", "地方", "驻外", "其他"]