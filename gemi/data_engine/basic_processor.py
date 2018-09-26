# db
from gemi.data_engine.database import get_db
from gemi.data_engine.extractor import FieldExtractor
from gemi.data_engine.util import TimeManager, Cleaner


class ItemProcessor:
    def __init__(self):
        self.db = get_db()
        # get links seen
        self.links_seen = self.db.yachts.distinct('link')

    def update_item(self, length, link, price, location, broker, sale_pending, item):
        # track earlier items
        if link in self.links_seen:
            self.update_already_existing_item(link, price, sale_pending)
            item = None
        else:
            # if seen first time
            self.links_seen.append(link)
            item = self.create_new_item(length, link, price, location, broker, item)

        return item

    @staticmethod
    def create_new_item(length, link, price, location, broker, item):
        # clean
        price, length, location, broker = Cleaner.clean_basic_fields(price, length, location, broker)
        todays_date = TimeManager.get_todays_date().isoformat()

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
                'crawled': todays_date,
                'last-updated': todays_date
            },
            'price': price
        }
        item.update(basic_fields)

        # add model and year
        model_and_year = FieldExtractor.get_model_and_year(link)
        item.update(model_and_year)

        return item

    def update_already_existing_item(self, link, price, sale_pending):

        updates = dict()
        todays_date = TimeManager.get_todays_date().isoformat()
        # get the item
        item = self.db.yachts.find_one({"link": link})
        # check the price
        last_price = item['price']

        if last_price != price:
            updates['status.price_changed'] = True
            updates['price'] = price
            updates['dates.price_changed'] = todays_date

        # check sale status
        if sale_pending:
            updates['status.sale_pending'] = True
            updates['dates.sale_pending'] = todays_date

        updates['updated'] = True

        # update only changed fields
        self.db.yachts.find_one_and_update(
            {'link': link},  # filter
            {
                '$set': updates,
                '$inc': {'days_on_market': 17}
            }
        )
