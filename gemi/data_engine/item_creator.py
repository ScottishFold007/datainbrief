from gemi.data_engine.field_extractor import FieldExtractor
from gemi.util.cleaner import Cleaner

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