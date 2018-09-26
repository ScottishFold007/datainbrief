# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo.errors import DuplicateKeyError


class DetailPipeline(object):
    def __init__(self):
        self.client = get_db_client()
        self.db = get_db()

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        try:
            self.db.yachts.update_one(
                {'link': item.link},
                {
                    '$set': {'detail': item.detail, 'hours': item.hours}
                }
            )
        except DuplicateKeyError:
            print('duplicate item')

        return item
