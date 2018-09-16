# time
import datetime


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
