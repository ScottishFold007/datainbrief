# -*- coding: utf-8 -*-

# Define your item processors here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from src.helpers import db_api
from src.helpers.new_item_factory import add_new_item
from src.helpers.item_updater import get_updates


class BasicPipeline(object):
    def __init__(self):
        db_api.check_removed_items()
        self.links_seen = db_api.get_distinct_items_by_key("link")

    def process_item(self, item, spider):
        link = item['link']
        if link in self.links_seen:
            saved_item = db_api.get_a_single_item_by_key({"link": link})
            updates = get_updates(item, saved_item)

            db_api.save_updated_item(link, updates)
        else:
            item = add_new_item(item)
            db_api.save_new_item(item)
        return item

    def close_spider(self, spider):
        db_api.check_removed_items()


class DetailPipeline(object):
    def process_item(self, item, spider):
        link = item['link']
        details = item['details']
        if 'engine_hours' in details:
            hours = item['engine_hours']
        else:
            hours = 'missing'
        db_api.save_details(link, details, hours)
        return item
