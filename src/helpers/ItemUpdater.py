from src.helpers import clean_price
from src.helpers import todays_date, str_to_date
from src import boats_database


class ItemUpdater(object):
    @staticmethod
    def is_already_updated(item):
        last_seen = str_to_date(item['dates']['last_seen'])
        if last_seen == todays_date:  # already updated today
            print(last_seen.isoformat(), 'already updated today')
            return True

    @classmethod
    def update_item(cls, item):

        link, price, sale_pending = item['link'], item['price'], item['sale_pending']

        saved_item = boats_database.get_a_single_item_by_key("link", link)

        if not saved_item:
            return True

        # check last update
        if cls.is_already_updated(saved_item):
            return True

        status_updates = {
            'dates.last_seen': todays_date,
            'status.updated': True,
            'status.removed': False
        }

        sale_updates = ItemUpdater.check_sale_status(sale_pending)
        price_updates = ItemUpdater.check_price_changes(saved_item, price)
        # merge dicts
        updates = {**status_updates, **price_updates, **sale_updates}

        boats_database.update_item(link, updates)

    @staticmethod
    def check_sale_status(sale_pending):
        sale_updates = {}
        if sale_pending:
            return {'status.sale_pending': True,
                    'dates.sale_pending': todays_date}
        return sale_updates

    @staticmethod
    def check_price_changes(item, price):
        last_price = item['price']
        price_updates = {}

        if last_price != price:
            price_updates = {
                'old_price': last_price,
                'price': clean_price(price),
                'dates.price_changed': todays_date,
                'status.price_changed': True
            }

        return price_updates
