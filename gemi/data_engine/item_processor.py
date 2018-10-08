from gemi.data_engine.field_extractor import FieldExtractor
from gemi.util.time_manager import TimeManager
from gemi.util.cleaner import Cleaner
from gemi.database import get_db

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


class ItemUpdater(object):
    @staticmethod
    def is_already_updated(item, todays_date):
        last_updated = TimeManager.str_to_date(item['dates']['last-updated'])
        if last_updated == todays_date:  # already updated today
            print(last_updated.isoformat(), 'already updated today')
            return True

    def update_already_existing_item(self, item, price, sale_pending, todays_date):
        updates = dict()

        if not item:
            return True

        # check last update
        if self.is_already_updated(item, todays_date):
            return True

        # check the price
        last_price = item['price']

        if last_price != price:
            updates['status.price_changed'] = True
            updates['price'] = Cleaner.clean_price(price)
            updates['dates.price_changed'] = todays_date

        # check sale status
        if sale_pending:
            updates['status.sale_pending'] = True
            updates['dates.sale_pending'] = todays_date

        updates['updated'] = True
        updates['status.removed'] = False
        updates['dates.last-updated'] = todays_date

        print('updated: ', updates)

        return updates


class NewItemCreator(object):
    @staticmethod
    def create_new_item(length, sub_link, link, price, location, broker, days_on_market, date):
        length, location, broker = Cleaner.remove_empty_chars_and_new_lines([length, location, broker])
        maker, model, year = FieldExtractor.get_maker_model_and_year(sub_link)
        city, state, country = FieldExtractor.extract_city_state_and_country_from_location(location)
        # fill in the item info
        item = {
            'length': length,
            'location': location,
            'city': city,
            'state': state,
            'country': country,
            'broker': broker,
            'link': link,
            'status': {
                'active': True,
                'updated': True,
                'removed': False,
                'sold': False,
                'sale-pending': False,
                'price-changed': False
            },
            'dates': {
                'crawled': date,
                'last-updated': date
            },
            'price': Cleaner.clean_price(price),
            'maker': maker,
            'model': model,
            'maker model': maker + model,
            'year': year,
            'days_on_market': days_on_market
        }

        print('new item: ', item)

        return item
