# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class QuoteItem(scrapy.Item):  # 所有Item都要继承scrapy.Item类
    text = scrapy.Field()  # 这个scrapy.Field()也是必须的，把它当成一个字段吧
    author = scrapy.Field()
    tags = scrapy.Field()
