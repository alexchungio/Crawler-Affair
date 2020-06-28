# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import os
import time
import csv

from scrapy import Request
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline


class CrawleraffairPipeline:
    def process_item(self, item, spider):
        return item


class ItemToTextPipeline():

    def __init__(self, file_path):
        self.path = file_path

    @classmethod
    def from_crawler(cls, crawler):
        file_path = crawler.settings.get('PATH')
        return cls(file_path=file_path)

    def open_spider(self, spider):
        spider_dir = os.path.join(self.path, spider.name)
        if os.path.exists(spider_dir) is False:
            os.makedirs(spider_dir)
        tmp_path = os.path.join(spider_dir, str(int(time.time())) + '.txt')
        self.fhd = open(tmp_path, 'w')

    def close_spider(self, spider):
        self.fhd.close()

    def process_item(self, item, spider):
        data_info = dict(item)
        vals = ','.join(data_info.values())
        self.fhd.write(vals)
        self.fhd.write('\n')
        return item

class ItemToCSVPipeline(object):
    def __init__(self, file_path):
        self.path = file_path

    @classmethod
    def from_crawler(cls, crawler):
        file_path = crawler.settings.get('PATH')
        return cls(file_path=file_path)

    def open_spider(self, spider):
        spider_dir = os.path.join(self.path, spider.name)
        if os.path.exists(spider_dir) is False:
            os.makedirs(spider_dir)
        tmp_path = os.path.join(spider_dir, str(int(time.time())) + '.csv')
        self.fhd = open(tmp_path, 'w')
        self.write = csv.writer(self.fhd)
        self.write.writerow(['spider_time', 'publish_time','title', 'label', 'content', 'url'])

    def close_spider(self, spider):
        self.fhd.close()

    def process_item(self, item, spider):

        item_list = [item['spider_time'], item['publish_time'], item['title'], item['label'], item['content'],
                     item['url']]
        self.write.writerow(item_list)
        return item