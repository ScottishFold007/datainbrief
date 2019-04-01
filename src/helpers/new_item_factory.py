from src.util.DateTime import todays_date
from src.helpers.field_extractor import get_maker_model_and_year, extract_city_state_and_country_from_location
from src.util.Cleaner import clean_price


def add_new_item(item):
    # add new fields
    maker_model_and_year = get_maker_model_and_year(item['link'])
    item.update(maker_model_and_year)
    city_state_and_country = extract_city_state_and_country_from_location(item['location'])
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

    return item

