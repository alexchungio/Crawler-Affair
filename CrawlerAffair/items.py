# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CrawlerAffairItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    spider_time = scrapy.Field()
    publish_time = scrapy.Field()
    title = scrapy.Field()
    label = scrapy.Field()
    content = scrapy.Field()
    url = scrapy.Field()


class ScrapyCodesItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
