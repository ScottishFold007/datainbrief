from gemi.util.cleaner import Cleaner
from gemi.database import db
from gemi.util.time_manager import date_now, str_to_date

collection_name = 'yachts'


class ItemUpdater(object):
    @staticmethod
    def is_already_updated(item):
        last_updated = str_to_date(item['dates']['last-updated'])
        if last_updated == date_now:  # already updated today
            print(last_updated.isoformat(), 'already updated today')
            return True

    @classmethod
    def update_already_existing_item(cls, link, price, sale_pending):
        updates = dict()

        item = db[collection_name].find_one({"link": link})

        if not item:
            return True

        # check last update
        if cls.is_already_updated(item):
            return True

        # check the price
        last_price = item['price']

        if last_price != price:
            updates['status.price_changed'] = True
            updates['price'] = Cleaner.clean_price(price)
            updates['dates.price_changed'] = date_now

        # check sale status
        if sale_pending:
            updates['status.sale_pending'] = True
            updates['dates.sale_pending'] = date_now

        updates['updated'] = True
        updates['status.removed'] = False
        updates['dates.last-updated'] = date_now

        print('updated: ', updates)

        return updates

    @staticmethod
    def save_updated_item(link, updates):
        # update only changed fields
        db.yachts.find_one_and_update(
            {'link': link},  # filter
            {
                '$set': updates,
                '$inc': {'days_on_market': 1}
            }
        )
