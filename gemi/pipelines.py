# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo.errors import DuplicateKeyError
from gemi.database import get_client_and_db
from gemi.data_engine.item_processor import ItemProcessor


class ItemPipeline(object):

    def __init__(self):
        self.client, db = get_client_and_db()
        self.processor = ItemProcessor(db)

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item_data, spider):
        self.processor.update_and_save_item_data(item_data)
        return True


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
