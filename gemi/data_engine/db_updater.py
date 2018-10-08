from gemi.util.time_manager import TimeManager

from gemi.database import get_db
from gemi.data_engine.item_creator import NewItemCreator
from gemi.data_engine.item_updater import ItemUpdater

from pymongo.errors import DuplicateKeyError


class DatabaseUpdater(object):
    base_url = 'https://www.yachtworld.com'
    collection_name = 'yachts'

    def __init__(self):
        self.db = get_db()
        # get links seen
        self.links_seen = self.db[self.collection_name].distinct('link')
        self.todays_date = TimeManager.get_todays_date().isoformat()
        self.updater = ItemUpdater()
        self.creator = NewItemCreator()

    def set_initial_status(self):
        # set all as not updated first
        self.db[self.collection_name].update_many(
            {"dates.last-updated": {"$lt": self.todays_date}},  # select unsold items
            {
                '$set': {'status.updated': False}
            }
        )

    def update_item_data(self, item_data):
        length, sub_link, price, location, broker, sale_pending, days_on_market = item_data

        link = self.base_url + sub_link
        if link in self.links_seen:  # seen before
            item = self.db[self.collection_name].find_one({"link": link})
            updates = self.updater.update_already_existing_item(item, price, sale_pending, self.todays_date)
            self.save_updated_item(link, updates)

        else:  # seen first time
            self.links_seen.append(link)
            item = self.creator.create_new_item(length, sub_link, link, price, location, broker, days_on_market,
                                                self.todays_date)
            self.save_new_item(item)

    def save_new_item(self, item):
        try:
            # write new item to the db
            self.db[self.collection_name].insert_one(dict(item))
        except DuplicateKeyError:
            print('duplicate item')

    def record_removed_items(self):
        updates = dict()
        updates['status.removed'] = True
        updates['dates.removed'] = self.todays_date
        # get untouched items and update
        self.db.yachts.update_many(
            {'status.updated': False},
            {'$set': updates}
        )

    def save_updated_item(self, link, updates):
        # update only changed fields
        self.db[self.collection_name].find_one_and_update(
            {'link': link},  # filter
            {
                '$set': updates,
                '$inc': {'days_on_market': 1}
            }
        )




