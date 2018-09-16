# time
import datetime
# util
from urllib.parse import urlencode
from collections import OrderedDict


def clean_basic_fields(price, length, location, broker):
    # clean the fields
    cleaned_fields = list(map(lambda field: " ".join(field.split()), [price, length, location, broker]))
    return cleaned_fields


def get_price_and_status_lists(price):
    # timestamp the crawl
    today = get_todays_date().isoformat()
    price_list = [(price, today)]
    status_list = [('active', today)]

    return {'price_list': price_list,
            'status_list': status_list
            }


def get_model_and_year(link):
    # get the year and model from the link
    split_link = link.split('/')
    year, model = split_link[2], split_link[3]

    return {
        'model': model,
        'year': year,
    }


def remove_empty_prices(prices):
    for i, price in enumerate(prices):
        clean_price = price.replace('\n', '').strip()
        if clean_price == '':
            prices.pop(i)
    return prices


def extract_hours_from_details(details):
    if 'hours' in details:
        pass
    else:
        return 'no hour info in details'


def get_todays_date():
    return datetime.datetime.now().date()


def check_price_change(item, price):
    today = get_todays_date()
    try:
        price_list = item['price_list']
        last_price = price_list[-1][0]  # get the value of the last price (price,time) tuples
    except KeyError:
        # remove the price and return its value
        last_price = item.pop('price', None)
        week_ago = today - datetime.timedelta(days=7)
        # create price list
        price_list = [(last_price, week_ago.isoformat())]

    if last_price != price:
        new_price = (price, today.isoformat())
        price_list.append(new_price)

    return price_list


def check_status_change(item, sale_pending):
    today = get_todays_date()
    week_ago = today - datetime.timedelta(days=7)
    try:
        sale_status = item['sale_status']
    except KeyError:
        sale_status = [('active', week_ago.isoformat())]
    if sale_pending:
        new_status = ('sale_pending', today.isoformat())
        sale_status.append(new_status)

    return sale_status


# query generator
def generate_base_query_urls():
    urls = list()
    days = list()

    root_search_url = 'https://www.yachtworld.com/core/listing/cache/searchResults.jsp'

    # default query
    base_query_parameters = {
        'fromLength': 25,
        'toLength': '',
        'fromYear': 1995,
        'toYear': '',
        'fromPrice': 20000,
        'toPrice': 8000000,
        'luom': 126,  # units feet, meter=127
        'currencyid': 100,  # US dollar
        'ps': 300  # entries per page
    }

    within_x_days = [(1, 1535580789155), (3, 1535407989155), (7, 1535062389155),
                     (14, 1534457589155), (30, 1533075189155), (60, 1530483189155), (100, '')]

    within_x_days = OrderedDict(within_x_days)

    # generate queries for all day options
    for day, pbsint in within_x_days.items():
        base_query_parameters['pbsint'] = pbsint
        query_string = urlencode(base_query_parameters, 'utf-8')
        query_url = root_search_url + '?' + query_string
        urls.append(query_url)
        days.append(day)

    return urls, days
