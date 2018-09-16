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
