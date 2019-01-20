# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
from scrapy import Item, Field


class GemiItem(Item):
    model = Field()
    year = Field()
    link = Field()
    location = Field()
    length = Field()
    broker = Field()
    status = Field()
    detail = Field()
    hours = Field()