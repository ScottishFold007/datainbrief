# helpers
from gemi.pipelines.field_extractor import FieldExtractor
from gemi.util.cleaner import Cleaner
# db
from gemi.database import db, collection_name
# date
from gemi.util.time_manager import date_now
# external packages
from pymongo.errors import DuplicateKeyError


class NewItemCreator(object):
    @staticmethod
    def create_new_item(length, link, price, location, broker, days_on_market):
        length, location, broker = Cleaner.remove_empty_chars_and_new_lines([length, location, broker])
        maker, model, year = FieldExtractor.get_maker_model_and_year(link)
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
                'crawled': date_now,
                'last-updated': date_now
            },
            'price': Cleaner.clean_price(price),
            'maker': maker,
            'model': model,
            'maker model': maker + model,
            'title': maker + model + year + length,
            'year': year,
            'days_on_market': days_on_market
        }

        print('new item: ', item)

        return item

    @staticmethod
    def save_new_item(item):
        try:
            # write new item to the db
            db[collection_name].insert_one(dict(item))
        except DuplicateKeyError:
            print('duplicate item')
