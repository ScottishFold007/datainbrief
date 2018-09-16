# time
import datetime


class FieldProcessor(object):
    @staticmethod
    def clean_basic_fields(price, length, location, broker):
        # clean the fields
        cleaned_fields = list(map(lambda field: " ".join(field.split()), [price, length, location, broker]))
        return cleaned_fields

    @staticmethod
    def get_price_and_status_lists(price):
        # timestamp the crawl
        date = datetime.datetime.now().date()
        # current_time = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        price_list = [(price, date)]
        status_list = [('active', date)]

        return {'price_list': price_list,
                'status_list': status_list
                }

    @staticmethod
    def get_model_and_year(link):
        # get the year and model from the link
        split_link = link.split('/')
        year, model = split_link[2], split_link[3]

        return {
            'model': model,
            'year': year,
        }

    @staticmethod
    def remove_empty_prices(prices):
        for i, price in enumerate(prices):
            clean_price = price.replace('\n', '').strip()
            if clean_price == '':
                prices.pop(i)
        return prices

    @staticmethod
    def extract_hours_from_details(details):
        if 'hours' in details:
            pass
        else:
            return 'no hour info in details'

    @staticmethod
    def check_price_change(item, price):
        today = datetime.datetime.now().date()
        try:
            price_list = item['price_list']
            last_price = price_list[-1][0]  # get the value of the last price (price,time) tuples
        except KeyError:
            # remove the price and return its value
            last_price = item.pop('price', None)
            week_ago = today - datetime.timedelta(days=7)
            # create price list
            price_list = [(last_price, week_ago)]

        if last_price != price:
            new_price = (price, today)
            price_list.append(new_price)

        return price_list
