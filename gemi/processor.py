# db
from gemi.database import get_db
from gemi.extractor import FieldExtractor
from gemi.util import TimeManager, Cleaner


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
                '$set': {'price_list': price_list, 'sale_status': sale_status, 'updated': True, 'removed': False},
                '$inc': {'days_on_market': 8}
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
            week_ago = TimeManager.get_date_of_x_days_ago(7)
            # create price list
            price_list = [(last_price, week_ago.isoformat())]

        if last_price != price:
            new_price = (price, today.isoformat())
            price_list.append(new_price)

        return price_list

    @staticmethod
    def check_status_change(item, sale_pending):
        today = TimeManager.get_todays_date()
        week_ago = TimeManager.get_date_of_x_days_ago(7)
        try:
            sale_status = item['sale_status']
        except KeyError:
            sale_status = [('active', week_ago.isoformat())]
        if sale_pending:
            new_status = ('sale_pending', today.isoformat())
            sale_status.append(new_status)

        return sale_status
