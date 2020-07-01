# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import os
import time
import scrapy
from scrapy import signals
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import ElementNotInteractableException

from CrawlerAffair.spiders.xinhua import XinhuaPoliticsSpider


class CrawleraffairSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class CrawleraffairDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

class XinhuaMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.
    def __init__(self, delay_time):
        self.delay_time = float(delay_time)

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        delay_time = crawler.settings.get('DELAY_TIME')
        s = cls(delay_time=delay_time)
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)

        return s

    def process_request(self, request, spider):

        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        # if request.url in ["http://www.news.cn/politics/index.htm", "http://www.xinhuanet.com/politics/xgc.htm",
        #                    'http://www.news.cn/local/index.htm', 'http://www.news.cn/local/wgzg.htm']:
        if request.url in ['http://www.news.cn/local/index.htm']:
            spider.browser.get(url=request.url)
            more_btn = spider.browser.find_elements_by_xpath('//*[@class="moreBtn"]')
            more_link = spider.browser.find_elements_by_xpath('//*[@class ="moreLink"]')

            if len(more_btn) != 0:
                click_element = spider.browser.find_element_by_xpath('//*[@class="moreBtn"]')
            else:
                click_element = spider.browser.find_element_by_xpath('//*[@class ="moreLink"]')


            if len(more_btn) or len(more_link) != 0:
                while True:
                    try:
                        load_more = click_element
                        load_more.click()
                        time.sleep(self.delay_time)
                    except ElementNotInteractableException:
                        break
            # return selenium response
            html = spider.browser.page_source
            return scrapy.http.HtmlResponse(url=spider.browser.current_url, body=html.encode(), encoding="utf-8",
                                            request=request)


    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        # chrome_options = Options()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        # chrome_options.add_argument('--no-sandbox')

        # if request.url in ["http://www.news.cn/politics/index.htm", "http://www.xinhuanet.com/politics/xgc.htm",
        #                    'http://www.news.cn/local/index.htm', 'http://www.news.cn/local/wgzg.htm']:
        #     spider.browser.get(url=request.url)
        #     load_more = spider.browser.find_elements_by_xpath('//*[@class="moreBtn"]')
        #     if len(load_more) != 0:
        #         while True:
        #             try:
        #                 load_more = spider.browser.find_element_by_xpath('//*[@class="moreBtn"]')
        #                 load_more.click()
        #                 time.sleep(self.delay_time)
        #             except ElementNotInteractableException:
        #                 break
        #     # return selenium response
        #     html = spider.browser.page_source
        #     return scrapy.http.HtmlResponse(url=spider.browser.current_url, body=html.encode(), encoding="utf8", request=request)  # 参数url指当前浏览器访问的url(通过current_url方法获取), 在这里参数url也可以用request.url

        response = scrapy.http.HtmlResponse(url=response.url, body=response.body, encoding="utf-8")
        return response



    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
