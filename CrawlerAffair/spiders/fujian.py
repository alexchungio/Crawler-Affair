#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------
# @ File       : fujian.py
# @ Description:  
# @ Author     : Alex Chung
# @ Contact    : yonganzhong@outlook.com
# @ License    : Copyright (c) 2017-2018
# @ Time       : 2020/7/8 下午4:51
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
from selenium.common.exceptions import ElementNotInteractableException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from CrawlerAffair.utils import process_title, process_time, process_content, process_label
from CrawlerAffair.items import CrawlerAffairItem
from CrawlerAffair.utils import scroll


# 无头浏览器设置
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument('--no-sandbox')
# chrome_options.add_argument("window-size=1024,768")

driver_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'libs', 'chromedriver')


class FujianInfoSpider(scrapy.Spider):
    name = "fujian_info_spider"
    urls = ["http://zwfw.fujian.gov.cn/"]
    allowed_domains = ["fujian.gov.cn"]
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
        sel = Selector(response)

        self.browser.get(response.url)
        # show as list
        # wait = WebDriverWait(self.browser, 1)
        # wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@class="last-notice-top"]/a')))
        time.sleep(1)
        info_page = self.browser.find_element_by_xpath('//div[@class="last-notice-top"]/a')
        self.browser.execute_script("arguments[0].click();", info_page)
        time.sleep(0.5)
        page_list = self.browser.find_elements_by_xpath('//ul[@class="el-pager"]/li')
        #
        for i in range(int(page_list[-1].text)):
            news_element_list = self.browser.find_elements_by_xpath('//table/tbody/tr/td/a')
            news_list = [news.get_attribute("href") for news in news_element_list]
            # yield scrapy.Request(url=sel.response.url, meta={"news_list": news_list}, callback=self.parse_sub_page,
            #                      dont_filter=True)
            for news_url in news_list:
                yield scrapy.Request(url=news_url, meta=None, callback=self.parse_detail)
            next_page = self.browser.find_element_by_xpath('//*[@class="btn-next"]/i')
            self.browser.execute_script("arguments[0].click();", next_page)
            time.sleep(0.5)

    # def parse_sub_page(self, response):
    #
    #     news_list = response.meta["news_list"]
    #

    def parse_detail(self, response):

        sel = Selector(response)

        news_item = CrawlerAffairItem()

        spider_time = str(int(time.time()))
        # '/html/body/div[2]/div[3]/div/div[1]'
        self.sub_browser.get(response.url)
        # wait = WebDriverWait(self.browser, 1)
        # wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@class="inner-content"]/div[@class="show_title"]')))
        time.sleep(0.5)
        publish_time_element = self.sub_browser.find_elements_by_xpath('//div[@class="inner-content"]/div[@class="show_time"]/div/div[2]')
        publish_time = [time.text for time in publish_time_element]
        title_element = self.sub_browser.find_elements_by_xpath('//div[@class="inner-content"]/div[@class="show_title"]')
        title = [t.text for t in title_element]
        contents_element = self.sub_browser.find_elements_by_xpath('//div[@class="inner-content"]/div[@class="show_content"]/p')
        contents = [c.text for c in contents_element]
        labels = []
        news_item["spider_time"] = spider_time
        news_item["publish_time"] = process_time(publish_time)
        news_item["title"] = process_title(title)
        news_item["label"] = process_label(labels)
        news_item["content"] = process_content(contents)
        news_item['url'] = sel.response.url.strip()

        return news_item