# -*- coding: utf-8 -*-
import scrapy


class QuotesSpider(scrapy.Spider):  # 自定义的spider类必须继承scrapy.Spider类
    name = "quotes"  # 必须属性：用来区分不同的spider
    start_urls = [
        'http://quotes.toscrape.com/page/1/',
        'http://quotes.toscrape.com/page/2/',
    ]

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = 'quotes-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
