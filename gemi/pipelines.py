# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import TEXT
from pymongo.errors import DuplicateKeyError
from scrapy.exceptions import DropItem

from gemi.database import get_db_client




# first duplicate check, only checks duplicates in the current job
class DuplicatesPipeline(object):

    def __init__(self):
        self.links_seen = set()

    def process_item(self, item, spider):
        if item['link'] in self.links_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.links_seen.add(item['link'])
            return item


class MongoPipeline(object):

    def __init__(self):
        self.client = get_db_client()
        self.db = self.client['gemi']  # db name

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        # how to update that index
        self.client.close()

    def process_item(self, item, spider):
        try:
            self.db.yachts.insert_one(dict(item))
        except DuplicateKeyError:
            print('duplicate item')

        return item
