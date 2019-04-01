from src.util.DateTime import todays_date
from src.helpers.FieldExtractor import FieldExtractor
from src.util.Cleaner import clean_price
from src.helpers import db_api


class ItemCreator(object):
    @staticmethod
    def add_new_item(item):
        # add new fields
        maker_model_and_year = FieldExtractor.get_maker_model_and_year(item['link'])
        item.update(maker_model_and_year)
        city_state_and_country = FieldExtractor.extract_city_state_and_country_from_location(item['location'])
        item.update(city_state_and_country)

        price = item['price']
        item['price'] = clean_price(price)
        new_data = {
            'status': {
                'removed': False,
                'sale_pending': False,
                'price_changed': False,

            },
            'dates': {
                'first_seen': todays_date,
                'last_seen': todays_date
            }
        }
        item.update(new_data)

        db_api.save_new_item(item)
