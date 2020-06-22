#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------
# @ File       : run.py.py
# @ Description:  
# @ Author     : Alex Chung
# @ Contact    : yonganzhong@outlook.com
# @ License    : Copyright (c) 2017-2018
# @ Time       : 2020/6/22 上午11:11
# @ Software   : PyCharm
#-------------------------------------------------------

import os
import sys
from scrapy.commands.crawl import Command
from scrapy.cmdline import execute
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor
from scrapy.utils.log import configure_logging

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":

    # Command().run(args=["scrapy crawl itcast"], opts="-o teacher.csv")

    # method 1 execute
    # execute(argv=["scrapy", "crawl", "douban_book"])

    # method 2 CrawlerProcess（recommend）
    process = CrawlerProcess(get_project_settings())
    process.crawl("china_spide", domain={"china.com.cn"})
    process.start()