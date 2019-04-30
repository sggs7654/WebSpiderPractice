# -*- coding: UTF-8 -*-

import scrapy


class QuotesSpider(scrapy.Spider):  # 这是一段Spider代码，因为它继承了scrapy.Spider类
    name = 'quotes'  # name属性用来区分不同的Spider
    start_urls = [  # 初始请求列表
        'http://quotes.toscrape.com/tag/humor/',
    ]

    def parse(self, response):  # 定义了Spider的解析规则
        for quote in response.css('div.quote'):  # css选择器：选择class="quote" 的div元素。
            yield {  # 返回一个生成器
                'text': quote.css('span.text::text').get(),  # 更多选择器用法见：https://docs.scrapy.org/en/latest/topics/selectors.html
                'author': quote.xpath('span/small/text()').get(),
            }

        next_page = response.css('li.next a::attr("href")').get() 
        if next_page is not None:
            yield response.follow(next_page, self.parse)  # 【这一句的意思还没搞懂，可能要在response的api里找找】