# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class GemiItem(Item):
    # define the fields for your item here like:
    model = Field()
    year = Field()
    price = Field()
    link = Field()
    location = Field()
    length = Field()
    broker = Field()


