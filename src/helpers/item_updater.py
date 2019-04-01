from src.util.Cleaner import clean_price
from src.util.DateTime import todays_date, str_to_date


def is_already_updated(item):
    last_seen = str_to_date(item['dates']['last_seen'])
    if last_seen == todays_date:  # already updated today
        print(last_seen.isoformat(), 'already updated today')
        return True


def check_sale_status(sale_pending):
    sale_updates = {}
    if sale_pending:
        return {'status.sale_pending': True,
                'dates.sale_pending': todays_date}
    return sale_updates


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


def get_updates(item, saved_item):
    price, sale_pending = item['price'], item['sale_pending']

    if not saved_item:
        return True

    # check last update
    if is_already_updated(saved_item):
        return True

    status_updates = {
        'dates.last_seen': todays_date,
        'status.updated': True,
        'status.removed': False
    }

    price_updates = check_price_changes(saved_item, price)
    sale_updates = check_sale_status(sale_pending)

    # merge dicts
    updates = {**status_updates, **price_updates, **sale_updates}

    return updates
