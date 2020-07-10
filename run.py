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

from CrawlerAffair.spiders.china import ChinaAffairSpider, ChinaNewsSpider
from CrawlerAffair.spiders.fujian import FujianInfoSpider

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":

    # Command().run(args=["scrapy crawl itcast"], opts="-o teacher.csv")

    # method 1 execute
    # execute(argv=["scrapy", "crawl", "douban_book"])

    # method 2 CrawlerProcess（recommend）
    process = CrawlerProcess(get_project_settings())

    # process.crawl(ChinaNewsSpider, domain={"china.com.cn"})
    # process.crawl(ChinaAffairSpider, domain={"china.com.cn"})

    # process.crawl("china_news_spider", domain={"china.com.cn"})
    # process.crawl("china_affair_spider", domain={"china.com.cn"})
    # process.crawl("china_opinion_spider", domain={"china.com.cn"})
    # process.crawl("china_theory_spider", domain={"china.com.cn"})
    #
    # process.crawl("renmin_politics_spider", domain={"china.com.cn"})

    # process.crawl("xinhua_politics_spider", domain={"news.cn"})
    # process.crawl("xinhua_local_spider", domain={"news.cn"})
    # process.crawl("xinhua_legal_spider", domain={"news.cn"})
    # process.crawl("xinhua_renshi_spider", domain={"news.cn"})
    # process.crawl("xinhua_info_spider", domain={"news.cn"})
    # process.crawl("xinhua_siklroad_spider", domain={"news.cn"})

    # process.crawl("cctv_news_spider", domain={"cctv.com"})
    # process.crawl("cctv_shiping_spider", domain={"cctv.com"})
    # process.crawl("cctv_caijing_spider", domain={"cctv.com"})

    # process.crawl("chinadaily_china_spider", domain={"chinadaily.com.cn"})
    # process.crawl("chinadaily_world_spider", domain={"chinadaily.com.cn"})

    # process.crawl("thepaper_select_spider", domain={"thepaper.cn"})
    # process.crawl("thepaper_shishi_spider", domain={"thepaper.cn"})


    process.crawl(FujianInfoSpider, domain={"fujian.gov.cn"})
    process.start()

