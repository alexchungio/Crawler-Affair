#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------
# @ File       : egov.py
# @ Description:  
# @ Author     : Alex Chung
# @ Contact    : yonganzhong@outlook.com
# @ License    : Copyright (c) 2017-2018
# @ Time       : 2020/7/8 下午7:07
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
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 无头浏览器设置
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument('--no-sandbox')

driver_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'libs', 'chromedriver')


class EgovCommonSpider(scrapy.Spider):
    name = ""
    urls = ["http://www.e-gov.org.cn/channel-1.html"]
    allowed_domains = ["e-gov.org.cn"]
    custom_menu = []

    browser = None
    sub_browser = None

    def start_requests(self):
        # 'http://www.news.cn/local/wgzg.htm'
        urls = self.urls
        for url in urls:
            yield scrapy.Request(url=url, meta=None, callback=self.parse)

    # 整个爬虫结束后关闭浏览器
    def close(self, spider):
        self.browser.close()
        self.sub_browser.close()

    # parse web html
    def parse(self, response):

        self.browser.get(response.url)
        # self.browser.implicitly_wait(5)
        # time.sleep(1)

        menu_button_list = self.browser.find_elements_by_xpath(
            '//div[@id="search_list"]/table/tbody/tr/td/div/div/table/tbody/tr/td/div/a[contains(text(), "更多")]')
        # menu_button_list = sel.xpath('//*[@id="search_list"]/table/tbody/tr[1]/td[1]/div/div[2]/table/tbody/tr[11]/td/div/a').extract()
        # 'data-spm-anchor-id="C87458.PehgQlaw4J7u.EbPec9NH7wI8.1225"'
        # menu_url_list = [menu_button.get_attribute("href") for menu_button in menu_button_list]
        main_window = self.browser.current_window_handle
        for menu_button in menu_button_list:

            pre_all_window = self.browser.window_handles
            self.browser.execute_script("arguments[0].click();", menu_button)
            # time.sleep(1)
            # 针对新增页面进行处理（非原页面刷新）
            current_all_window = self.browser.window_handles
            for window in current_all_window:
                if window not in pre_all_window:
                    self.browser.switch_to.window(window)
                    time.sleep(0.5)
            page_label_element = self.browser.find_elements_by_xpath('//*[@id="pageLabel"]/label')
            if len(page_label_element) == 0:
                self.browser.switch_to_window(main_window)
                time.sleep(0.5)
                continue
            else:
                page_label = page_label_element[0].text
            num_page = int(page_label.split(r'/')[-1])
            # get page news list
            for index in range(1, num_page + 1):
                url = self.browser.current_url.replace('.html', f'-{index}.html')
                yield scrapy.Request(url=url, meta=None, callback=self.parse_sub_page, dont_filter=True)

            # back to main window
            self.browser.switch_to_window(main_window)
            time.sleep(0.5)

    def parse_sub_page(self, response):

        self.sub_browser.get(response.url)
        # time.sleep(0.5)
        wait = WebDriverWait(self.sub_browser, 2)
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="search_list"]/table/tbody/tr/td/a')))
        news_element_list = self.sub_browser.find_elements_by_xpath('//*[@id="search_list"]/table/tbody/tr/td/a')
        news_list = [news.get_attribute("href") for news in news_element_list]
        for news_url in news_list:
            # label = sel.xpath('//div[@class="v1000 clearfix bc"]/div[@class="fl w650"]/h1[@class="title]/span/text()')
            yield scrapy.Request(url=news_url, meta=None, callback=self.parse_detail)

    def parse_detail(self, response):

        news_item = CrawlerAffairItem()
        spider_time = str(int(time.time()))

        self.sub_browser.get(response.url)
        # time.sleep(0.5)
        # time.sleep(1)
        wait = WebDriverWait(self.sub_browser, 1)
        wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@id="text_block"]/div[@id="content_detail"]')))

        publish_time = self.sub_browser.find_element_by_xpath('//div[@id="text_block"]/div[@id="content_detail"]').text
        title_elements = self.sub_browser.find_elements_by_xpath('//div[@id="text_block"]/div[@class="title_bar"]')
        title = [t.text for t in title_elements]

        contents_element_1 = self.sub_browser.find_elements_by_xpath('//*[@id="content_detail"]/p')
        contents = [content.text for content in contents_element_1]
        contents_element_2 = self.sub_browser.find_elements_by_xpath('//*[@id="zoom"]/p')
        contents_2 = [content.text for content in contents_element_2]
        contents.extend(contents_2)
        contents_element_3 = self.sub_browser.find_elements_by_xpath('//*[@id="content_detail"]/table/tbody/tr/td/p')
        contents_3 = [content.text for content in contents_element_3]
        contents.extend(contents_3)
        contents_element_4 = self.sub_browser.find_elements_by_xpath('//*[@id="content_detail"]/font')
        contents_4 = [content.text for content in contents_element_4]
        contents.extend(contents_4)
        contents_element_5 = self.sub_browser.find_elements_by_xpath('//*[@id="content_detail"]')
        contents_5 = [content.text for content in contents_element_5]
        contents.extend(contents_5)
        contents_element_6 = self.sub_browser.find_elements_by_xpath(
            '//*[@id="content_detail"]/table/tbody/tr/td[@class="detail"]/p')
        contents_6 = [content.text for content in contents_element_6]
        contents.extend(contents_6)

        labels = []
        news_item["spider_time"] = spider_time
        news_item["publish_time"] = process_time(publish_time)
        news_item["title"] = process_title(title)
        news_item["label"] = process_label(labels)
        news_item["content"] = process_content(contents)
        news_item['url'] = response.url.strip()

        return news_item


class EgovNewsSpider(EgovCommonSpider):
    name = "egov_news_spider"
    urls = ["http://www.e-gov.org.cn/channel-1.html"]

    browser = webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)
    sub_browser = webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)

class EgovElectronicSpider(EgovCommonSpider):
    name = "egov_electronic_spider"
    urls = ["http://www.e-gov.org.cn/channel-1001.html"]

    browser = webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)
    sub_browser = webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)

class EgovInfoSpider(EgovCommonSpider):
    name = "egov_info_spider"
    urls = ["http://www.e-gov.org.cn/channel-1002.html"]

    browser = webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)
    sub_browser = webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)

class EgovComputerSpider(EgovCommonSpider):
    name = "egov_computer_spider"
    urls = ["http://www.e-gov.org.cn/channel-1004.html"]

    browser = webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)
    sub_browser = webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)

class EgovExhibitionSpider(EgovCommonSpider):
    name = "egov_exhibition_spider"
    urls = ["http://www.e-gov.org.cn/channel-1012.html"]

    browser = webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)
    sub_browser = webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)

class EgovPurchaseSpider(EgovCommonSpider):
    name = "egov_purchase_spider"
    urls = ["http://www.e-gov.org.cn/channel-1005.html"]

    browser = webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)
    sub_browser = webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)

class EgovCompanySpider(EgovCommonSpider):
    name = "egov_company_spider"
    urls = ["http://www.e-gov.org.cn/channel-1014.html"]

    browser = webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)
    sub_browser = webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)