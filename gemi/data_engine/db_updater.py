# project packages
from gemi.database import db
from gemi.data_engine.item_creator import NewItemCreator
from gemi.data_engine.item_updater import ItemUpdater
from gemi.util.time_manager import TimeManager

collection_name = 'yachts'
base_url = 'https://www.yachtworld.com'


class DatabaseUpdater(object):

    def __init__(self):
        # get links seen
        self.links_seen = db[collection_name].distinct('link')
        self.date = TimeManager.get_todays_date().isoformat()

    def set_initial_status(self):
        # set all as not updated first
        db[collection_name].update_many(
            {"dates.last-updated": {"$lt": self.date}},  # select unsold items
            {
                '$set': {'status.updated': False}
            }
        )

    def update_item_data(self, item_data):
        length, sub_link, price, location, broker, sale_pending, days_on_market = item_data

        link = base_url + sub_link
        # seen before
        if link in self.links_seen:
            updates = ItemUpdater.update_already_existing_item(price, sale_pending, self.date)
            ItemUpdater.save_updated_item(link, updates)
        # seen first time
        else:
            self.links_seen.append(link)
            item = NewItemCreator.create_new_item(length, sub_link, link,
                                                  price, location, broker,
                                                  days_on_market, self.date)
            NewItemCreator.save_new_item(item)

    def record_removed_items(self):
        updates = dict()
        updates['status.removed'] = True
        updates['dates.removed'] = self.date
        # get untouched items and update
        db.yachts.update_many(
            {'status.updated': False},
            {'$set': updates}
        )
