# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo.errors import DuplicateKeyError
from gemi.database import get_client_and_db


class DetailPipeline(object):
    client, db = get_client_and_db()

    def __init__(self):
        pass

    @classmethod
    def get_links(cls):
        return cls.db.yachts.distinct('link')

    @staticmethod
    def get_hours(description):
        # search for hours
        hour_in_various_languages = {'hour', 'time', 'stunde', 'ora', 'heure', 'uur', 'tunnin', 'timme', 'saat', 'hora'}
        if any(word in description for word in hour_in_various_languages):
            return True
        else:
            return False

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        hours_in_description = self.get_hours(item['detail'])
        if hours_in_description:
            item['hours'] = True
        else:
            item['hours'] = False
            del item['detail']

        try:
            self.db.detail.insert_one(item)
        except DuplicateKeyError:
            print('duplicate item')

        return item
