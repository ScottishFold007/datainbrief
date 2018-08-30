# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import re


class MongoPipeline(object):

    def __init__(self):
        pass

    def open_spider(self, spider):
        self.client = MongoClient(host='mongodb://<dbuser>:<dbpassword>@ds237072.mlab.com:37072/gemi',
                                  port=47450,
                                  username='roxy',
                                  password='gemicik1',
                                  authSource='gemi',
                                  authMechanism='SCRAM-SHA-1')

        self.db = self.client['gemi']  # db name

    def close_spider(self, spider):
        self.client.close()

    def get_year(self, model):
        try:
            year = model.split()[2]
        except IndexError as e:
            year = 'unknown'

        return year

    def process_item(self, item, spider):
        year = self.get_year(item['model'])
        item['year'] = year
        try:
            self.db.yachts.insert_one(dict(item))
            return item
        except DuplicateKeyError:
            return 'duplicate item'
