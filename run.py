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
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor
from scrapy.utils.log import configure_logging
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
# from scrapy.settings import Settings

from CrawlerAffair.spiders import china
from CrawlerAffair.spiders import  cctv
from CrawlerAffair.spiders import chinadaily
from CrawlerAffair.spiders import egov
from CrawlerAffair.spiders import fujian
from CrawlerAffair.spiders import gov
from CrawlerAffair.spiders import renmin
from CrawlerAffair.spiders import sina
from CrawlerAffair.spiders import thepaper
from CrawlerAffair.spiders import xinhua
from CrawlerAffair.spiders import qq


sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":

    # Command().run(args=["scrapy crawl itcast"], opts="-o teacher.csv")

    # method 1 execute
    # execute(argv=["scrapy", "crawl", "douban_book"])

    # method 2 CrawlerProcess（recommend）
    # process = CrawlerProcess(get_project_settings())
    # # renmin_process = CrawlerProcess(get_project_settings())
    #
    #
    #   # the script will block here until the last crawl call is finished
    #
    # # process.crawl(ChinaNewsSpider, domain={"china.com.cn"})
    # # process.crawl(ChinaAffairSpider, domain={"china.com.cn"})
    #
    # process.crawl("china_news_spider", domain={"china.com.cn"})
    # process.crawl("china_affair_spider", domain={"china.com.cn"})
    # process.crawl("china_opinion_spider", domain={"china.com.cn"})
    # process.crawl("china_theory_spider", domain={"china.com.cn"})
    #
    # process.crawl("renmin_politics_spider", domain={"people.com.cn"})
    #
    # process.crawl("xinhua_politics_spider", domain={"news.cn"})
    # process.crawl("xinhua_local_spider", domain={"news.cn"})
    # process.crawl("xinhua_legal_spider", domain={"news.cn"})
    # process.crawl("xinhua_renshi_spider", domain={"news.cn"})
    # process.crawl("xinhua_info_spider", domain={"news.cn"})
    # process.crawl("xinhua_siklroad_spider", domain={"news.cn"})
    #
    # process.crawl("cctv_news_spider", domain={"cctv.com"})
    # process.crawl("cctv_shiping_spider", domain={"cctv.com"})
    # process.crawl("cctv_caijing_spider", domain={"cctv.com"})
    #
    # process.crawl("chinadaily_china_spider", domain={"chinadaily.com.cn"})
    # process.crawl("chinadaily_world_spider", domain={"chinadaily.com.cn"})
    #
    # process.crawl("thepaper_select_spider", domain={"thepaper.cn"})
    # process.crawl("thepaper_shishi_spider", domain={"thepaper.cn"})
    #
    # process.crawl("fujian_info_spider", domain={"fujian.gov.cn"})
    #
    # process.crawl("egov_news_spider", domain={"e-gov.org.cn"})
    # process.crawl("egov_electronic_spider", domain={"e-gov.org.cn"})
    # process.crawl("egov_info_spider", domain={"e-gov.org.cn"})
    # process.crawl("egov_computer_spider", domain={"e-gov.org.cn"})
    # process.crawl("egov_exhibition_spider", domain={"e-gov.org.cn"})
    # process.crawl("egov_purchase_spider", domain={"e-gov.org.cn"})
    # process.crawl("egov_company_spider", domain={"e-gov.org.cn"})
    #
    # #
    # process.crawl("gov_yaowen_spider", domain={"gov.cn"})
    # process.crawl("gov_policy_spider", domain={"gov.cn"})
    # process.crawl("gov_lianbo_spider", domain={"gov.cn"})
    # process.crawl("gov_fabu_spider", domain={"gov.cn"})
    # process.crawl("gov_renmian_spider", domain={"gov.cn"})
    #
    # # process.crawl("lawlib_xinshi_spider", domain={"law-lib.com"})
    # # process.crawl("lawlib_minshi_spider", domain={"law-lib.com"})
    # # process.crawl("lawlib_xinzhen_spider", domain={"law-lib.com"})
    #
    # process.crawl("qq_news_spider", domain={"qq.com"})
    #
    # process.crawl("sina_news_spider", domain={"sina.com.cn"})
    # process.crawl("sina_sifa_news_spider", domain={"sina.com.cn"})
    # process.crawl("sina_sifa_publicity_spider", domain={"sina.com.cn"})
    #
    # process.start()

    # running the spiders sequentially by chaining the deferreds:
    configure_logging()
    settings = get_project_settings()
    runner = CrawlerRunner(settings=settings)

    @defer.inlineCallbacks
    def crawl():
        # china
        yield runner.crawl(china.ChinaNewsSpider)
        yield runner.crawl(china.ChinaTheorySpider)
        yield runner.crawl(china.ChinaAffairSpider)

        # cctv
        yield runner.crawl(cctv.CCTVShipingSpider)
        yield runner.crawl(cctv.CCTVNewsSpider)
        yield runner.crawl(cctv.CCTVCaijingSpider)

        # chinadaily
        yield runner.crawl(chinadaily.ChinadailyChinaSpider)
        yield runner.crawl(chinadaily.ChinadailyWorldSpider)

        # egov
        yield runner.crawl(egov.EgovExhibitionSpider)
        yield runner.crawl(egov.EgovInfoSpider)
        yield runner.crawl(egov.EgovElectronicSpider)
        yield runner.crawl(egov.EgovComputerSpider)
        yield runner.crawl(egov.EgovCompanySpider)
        yield runner.crawl(egov.EgovPurchaseSpider)
        yield runner.crawl(egov.EgovNewsSpider)

        # fujian
        yield runner.crawl(fujian.FujianInfoSpider)

        # gov
        yield runner.crawl(gov.GovFabuSpider)
        yield runner.crawl(gov.GovLianboSpider)
        yield runner.crawl(gov.GovPolicySpider)
        yield runner.crawl(gov.GovRenmianSpider)
        yield runner.crawl(gov.GovYaowenSpider)

        # renmin
        yield runner.crawl(renmin.RenminPoliticsSpider)

        # thepapaer
        yield runner.crawl(thepaper.ThepaperSelectSpider)
        yield runner.crawl(thepaper.ThepaperShishiSpider)

        # xinhua
        yield runner.crawl(xinhua.XinhuaSilkRoad)
        yield runner.crawl(xinhua.XinhuaInfoSpider)
        yield runner.crawl(xinhua.XinhuaRenshiSpider)
        yield runner.crawl(xinhua.XinhualegalSpider)
        yield runner.crawl(xinhua.XinhuaLocalSpider)
        yield runner.crawl(xinhua.XinhuaPoliticsSpider)

        # sina
        yield runner.crawl(sina.SinaNewsSpider)
        yield runner.crawl(sina.SinaSifaNewsSpider)
        yield runner.crawl(sina.SinaSifaPublicitySpider)
        # qq
        runner.crawl(qq.QQNewsSpider)
        reactor.stop()

    crawl()
    reactor.run()  # the script will block here until the last crawl call is finished
    print('Done!')


# scrapy Failed to establish a new connection: [Errno 111] Connection refused',)