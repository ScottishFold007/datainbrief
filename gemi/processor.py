# db
from gemi.database import get_db
from gemi.extractor import FieldExtractor
from gemi.util import TimeManager, Cleaner


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
            'crawled': todays_date,
            'status':{
                'active': True,
                'updated': True,
                'removed': False,
                'sold': False,
                'sale-pending': False,
                'price-changed': False
            },
            'price': price
        }
        item.update(basic_fields)

        # add model and year
        model_and_year = FieldExtractor.get_model_and_year(link)
        item.update(model_and_year)

        return item

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
                '$set': {'price_list': price_list, 'sale_status': sale_status, 'updated': True, 'removed': False},
                '$inc': {'days_on_market': 1}
            }
        )


class ChangeTracker:
    @staticmethod
    def check_price_change(item, price):
        today = TimeManager.get_todays_date()
        try:
            price_list = item['price_list']
            last_price = price_list[-1][0]  # get the value of the last price (price,time) tuples
        except KeyError:
            # remove the price and return its value
            last_price = item.pop('price', None)
            week_ago = TimeManager.get_date_of_x_days_ago(8)
            # create price list
            price_list = [(last_price, week_ago.isoformat())]

        if last_price != price:
            new_price = (price, today.isoformat())
            price_list.append(new_price)

        return price_list

    @staticmethod
    def check_status_change(item, sale_pending):
        today = TimeManager.get_todays_date()
        week_ago = TimeManager.get_date_of_x_days_ago(8)
        try:
            sale_status = item['sale_status']
        except KeyError:
            sale_status = [('active', week_ago.isoformat())]
        if sale_pending:
            new_status = ('sale_pending', today.isoformat())
            sale_status.append(new_status)

        return sale_status
