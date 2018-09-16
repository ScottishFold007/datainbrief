# time
import datetime
# util
from urllib.parse import urlencode
from collections import OrderedDict
# db
from gemi.database import get_db
from gemi.extractor import FieldExtractor
from gemi.util import Util


class ItemProcessor:
    def __init__(self):
        # init db
        self.db = get_db()
        # get links seen
        self.links_seen = self.db.yachts.distinct('link')
        self.set_initial_status()

    def set_initial_status(self):
        # set all as not updated first
        self.db.yachts.update_many(
            {},  # select all
            {
                '$set': {'updated': False}
            }
        )

    def update_item_info(self, length, link, price, location, broker, sale_pending, item_info):
        # track earlier items
        if link in self.links_seen:
            self.update_already_existing_item(link, price, sale_pending)
            return None

        # if seen first time
        self.links_seen.append(link)

        # clean
        price, length, location, broker = Cleaner.clean_basic_fields(price, length, location, broker)

        # fill in the item info
        basic_fields = {
            'length': length,
            'location': location,
            'broker': broker,
            'link': link,
            'updated': True,
            'removed': False
        }
        item_info.update(basic_fields)

        # add model and year
        model_and_year = FieldExtractor.get_model_and_year(link)
        item_info.update(model_and_year)

        # add price and status
        price_and_status = FieldExtractor.get_price_and_status_lists(price)
        item_info.update(price_and_status)

        return item_info

    def update_already_existing_item(self, link, price, sale_pending):
        # get the item
        item = self.db.yachts.find_one({"link": link})
        # check the price
        price_list = ChangeTracker.check_price_change(item, price)
        # check status
        sale_status = ChangeTracker.check_status_change(item, sale_pending)

        # update only changed fields
        self.db.yachts.find_one_and_update(
            {'link': link},  # filter
            {
                '$unset': {'price': ""},  # remove price field
                '$set': {'price_list': price_list, 'sale_status': sale_status, 'updated': True},
                '$inc': {'days_on_market': 7}
            }
        )


# STATIC METHODS
class Cleaner:
    @staticmethod
    def clean_basic_fields(price, length, location, broker):
        # clean the fields
        cleaned_fields = list(map(lambda field: " ".join(field.split()), [price, length, location, broker]))
        return cleaned_fields

    @staticmethod
    def remove_empty_prices(prices):
        for i, price in enumerate(prices):
            clean_price = price.replace('\n', '').strip()
            if clean_price == '':
                prices.pop(i)
        return prices


class ChangeTracker:
    @staticmethod
    def check_price_change(item, price):
        today = get_todays_date()
        try:
            price_list = item['price_list']
            last_price = price_list[-1][0]  # get the value of the last price (price,time) tuples
        except KeyError:
            # remove the price and return its value
            last_price = item.pop('price', None)
            week_ago = Util.get_date_of_x_days_ago(7)
            # create price list
            price_list = [(last_price, week_ago.isoformat())]

        if last_price != price:
            new_price = (price, today.isoformat())
            price_list.append(new_price)

        return price_list

    @staticmethod
    def check_status_change(item, sale_pending):
        today = Util.get_todays_date()
        week_ago = Util.get_date_of_x_days_ago(7)
        try:
            sale_status = item['sale_status']
        except KeyError:
            sale_status = [('active', week_ago.isoformat())]
        if sale_pending:
            new_status = ('sale_pending', today.isoformat())
            sale_status.append(new_status)

        return sale_status


class QueryGenerator:
    @staticmethod
    def generate_urls_for_search_queries():
        urls = list()
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

        return urls
