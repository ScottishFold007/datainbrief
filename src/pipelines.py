# -*- coding: utf-8 -*-

# Define your item processors here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from src import boats_database
from src.helpers.ItemCreator import ItemCreator
from src.helpers import ItemUpdater


class GemiPipeline(object):
    def __init__(self):
        boats_database.check_removed_items()
        self.links_seen = boats_database.get_distinct_links()

    def process_item(self, item, spider):
        if item['link'] in self.links_seen:
            ItemUpdater.update_item(item)
        else:
            ItemCreator.add_new_item(item)
        return item

    def close_spider(self, spider):
        boats_database.check_removed_items()


class DetailPipeline(object):
    def process_item(self, item, spider):
        link = item['link']
        details = item['details']
        boats_database.save_details(link, details)
        return item