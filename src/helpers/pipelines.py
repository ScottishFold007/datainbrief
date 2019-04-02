# -*- coding: utf-8 -*-

# Define your item processors here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from src.db import db_api
from src.helpers.new_item_factory import add_new_item
from src.helpers.item_updater import get_updates
from src.models.ml import predict_price
from src.util.Cleaner import get_lower


class BasicPipeline(object):
    def __init__(self):
        db_api.check_removed_items()
        self.links_seen = db_api.get_distinct_items_by_key("link")

    def process_item(self, item, spider):
        link = item['link']

        if link in self.links_seen:
            saved_item = db_api.get_a_single_item_by_key({"link": link})
            updates = get_updates(item, saved_item)
            db_api.update_and_increment_day(link, updates)
        else:
            item = add_new_item(item)
            item = get_lower(item)
            feature_list = ['hours', 'length', 'year', 'model']
            predicted_price = predict_price(features)
            db_api.save_new_item(item)

        return item

    def close_spider(self, spider):
        db_api.check_removed_items()


class DetailPipeline(object):
    def process_item(self, item, spider):
        link = item.pop('link')

        if 'engine_hours' in item['details']:
            item['hours'] = item['details']['engine_hours']

        db_api.update_item(link, item)

        return item

    def close_spider(self, spider):
        db_api.check_removed_items()
