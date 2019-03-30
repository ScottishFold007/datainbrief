from src.helpers import todays_date, DataFieldExtractor
from src.helpers import clean_price
from src import boats_database


class ItemCreator(object):
    @staticmethod
    def add_new_item(item):
        # add new fields
        maker_model_and_year = DataFieldExtractor.get_maker_model_and_year(item['link'])
        item.update(maker_model_and_year)
        city_state_and_country = DataFieldExtractor.extract_city_state_and_country_from_location(item['location'])
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

        boats_database.save_new_item(item)
