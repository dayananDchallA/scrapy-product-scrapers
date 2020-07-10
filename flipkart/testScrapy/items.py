# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TestscrapyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = scrapy.Field()
    asin = scrapy.Field()
    rating = scrapy.Field()
    image = scrapy.Field()
    users_rated = scrapy.Field()
    listed_price = scrapy.Field()
    actual_price = scrapy.Field()
    specs = scrapy.Field()
    price = scrapy.Field()
    currency = scrapy.Field()
