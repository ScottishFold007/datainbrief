from gemi.util.cleaner import Cleaner
from gemi.database import db, collection_name
from gemi.util.time_manager import date_now, str_to_date


class ItemUpdater(object):
    @staticmethod
    def is_already_updated(item):
        last_updated = str_to_date(item['dates']['last_updated'])
        if last_updated == date_now:  # already updated today
            print(last_updated.isoformat(), 'already updated today')
            return True

    @classmethod
    def update_already_existing_item(cls, link, price, sale_pending):

        item = db[collection_name].find_one({"link": link})

        if not item:
            return True

        # check last update
        if cls.is_already_updated(item):
            return True

        status_updates = {
            'dates.last_updated': date_now,
            'status.updated': True,
            'status.removed': False,
            'status.active': True
        }

        price_updates = ItemUpdater.check_price_changes(item, price)
        sale_updates = ItemUpdater.check_sale_status(sale_pending)

        # merge dicts
        updates = {**status_updates, **price_updates, **sale_updates}

        print('updated: ', updates)

        return updates

    @staticmethod
    def check_sale_status(sale_pending):
        if sale_pending:
            return {'status.sale_pending': True,
                    'dates.sale_pending': date_now}

    @staticmethod
    def check_price_changes(item, price):
        last_price = item['price']
        if last_price != price:
            price_updates = {
                'price': Cleaner.clean_price(price),
                'dates.price_changed': date_now,
                'status.price_changed': True
            }

            try:
                old_prices = item['old_prices']
                price_updates['old_prices'] = old_prices.append(last_price)
            except KeyError:
                price_updates['old_prices'] = [last_price]
        else:
            price_updates = {}
        return price_updates

    @staticmethod
    def save_updated_item(link, updates):
        # update only changed fields
        db[collection_name].find_one_and_update(
            {'link': link},  # filter
            {
                '$set': updates,
                '$inc': {'days_on_market': 1}
            }
        )
