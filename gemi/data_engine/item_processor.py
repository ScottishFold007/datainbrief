# db
from gemi.data_engine.field_extractor import FieldExtractor
from gemi.data_engine.util import TimeManager, Cleaner
from pymongo.errors import DuplicateKeyError
from gemi.database import get_client_and_db


class ItemProcessor:

    def __init__(self, ):
        self.client, self.db = get_client_and_db()
        self.collection_name = 'yachts'
        # get links seen
        self.links_seen = self.db[self.collection_name].distinct('link')
        self.todays_date = TimeManager.get_todays_date().isoformat()

    def close_spider(self, spider):
        self.client.close()

    def set_initial_status(self):
        # set all as not updated first
        self.db[self.collection_name].update_many(
            {"dates.last-updated": {"$lt": self.todays_date}},  # select unsold items
            {
                '$set': {'status.updated': False}
            }
        )

    def update_and_save_item_data(self, item_data):
        length, link, price, location, broker, sale_pending, days_on_market = item_data
        # track earlier items
        if link in self.links_seen:
            self.update_already_existing_item(link, price, sale_pending)
        else:
            # if seen first time
            self.links_seen.append(link)
            self.create_new_item(length, link, price, location, broker, days_on_market)

    def create_new_item(self, length, link, price, location, broker, days_on_market):
        item = dict()
        item['days_on_market'] = days_on_market
        # clean
        price, length, location, broker = Cleaner.clean_basic_fields(price, length, location, broker)

        # fill in the item info
        basic_fields = {
            'length': length,
            'location': location,
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
                'crawled': self.todays_date,
                'last-updated': self.todays_date
            },
            'price': price
        }
        item.update(basic_fields)

        # add model and year
        model_and_year = FieldExtractor.get_model_and_year(link)
        item.update(model_and_year)

        # self.save_new_item(item)

    def update_already_existing_item(self, link, price, sale_pending):

        updates = dict()
        # get the item
        item = self.db[self.collection_name].find_one({"link": link})
        # check the price
        last_price = item['price']

        if last_price != price:
            updates['status.price_changed'] = True
            updates['price'] = price
            updates['dates.price_changed'] = self.todays_date

        # check sale status
        if sale_pending:
            updates['status.sale_pending'] = True
            updates['dates.sale_pending'] = self.todays_date

        updates['updated'] = True
        updates['status.removed'] = False
        updates['dates.last-updated'] = self.todays_date

        # self.save_updated_item(link, updates)

    def save_new_item(self, item):
        try:
            # write new item to the db
            self.db[self.collection_name].insert_one(dict(item))
        except DuplicateKeyError:
            print('duplicate item')

    def save_updated_item(self, link, updates):
        # update only changed fields
        self.db[self.collection_name].find_one_and_update(
            {'link': link},  # filter
            {
                '$set': updates,
                '$inc': {'days_on_market': 17}
            }
        )

    def record_removed_items(self):
        updates = dict()
        updates['status.removed'] = True
        updates['dates.removed'] = self.todays_date
        # get untouched items and update
        self.db.yachts.update_many(
            {'status.updated': False},
            {'$set': updates}
        )
