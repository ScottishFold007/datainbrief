# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo.errors import DuplicateKeyError
from scrapy.exceptions import DropItem

from gemi.database import get_db_client, get_db
from gemi.processor import get_todays_date

# only checks duplicates in the current job
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
        self.db = get_db()

    def open_spider(self, spider):
        pass

    def record_removed_items(self):
        today = get_todays_date().isoformat()
        # get untouched items
        not_updated_items = self.db.yachts.find({'updated': False})
        # update info for every item
        for item in not_updated_items:
            try:
                sale_status = item['sale_status']
            except KeyError:
                sale_status = list()

            sale_status.append(('sold', today))
            self.db.yachts.update_one(
                {'link': item['link']},
                {
                    '$set': {'removed': True, 'sale_status': sale_status}
                }
            )

    def close_spider(self, spider):
        # self.record_removed_items()
        self.client.close()

    def process_item(self, item, spider):
        try:
            self.db.yachts.insert_one(dict(item))
        except DuplicateKeyError:
            print('duplicate item')

        return item
