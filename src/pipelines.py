# -*- coding: utf-8 -*-

# Define your item processors here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from src.db import db
from src.helpers.ItemCreator import ItemCreator
from src.helpers import ItemUpdater


class BasicPipeline(object):
    def __init__(self):
        db.check_removed_items()
        self.links_seen = db.get_distinct_items_by_key("link")

    def process_item(self, item, spider):
        if item['link'] in self.links_seen:
            ItemUpdater.update_item(item)
        else:
            ItemCreator.add_new_item(item)
        return item

    def close_spider(self, spider):
        db.check_removed_items()


class DetailPipeline(object):
    def process_item(self, item, spider):
        link = item['link']
        details = item['details']
        if 'engine_hours' in details:
            hours = item['engine_hours']
        else:
            hours = 'missing'
        db.save_details(link, details, hours)
        return item
