from gemi.util import TimeManager
from gemi.util import Cleaner


class FieldExtractor:
    # basic field selectors
    link_selector = 'div.make-model a::attr(href)'
    length_selector = 'div.make-model a span.length::text'
    price_selector = 'div.price::text'
    location_selector = 'div.location::text'
    sale_pending = 'div.location span.active_field'
    broker_selector = 'div.broker::text'

    def extract_fields(self, page):
        # parse fields
        lengths = page.css(self.length_selector).extract()
        links = page.css(self.link_selector).extract()

        prices = page.css(self.price_selector).extract()
        # remove empty prices
        prices = Cleaner.remove_empty_prices(prices)

        locations = page.css(self.location_selector).extract()
        brokers = page.css(self.broker_selector).extract()
        sale_pending_fields = page.css(self.sale_pending).extract()

        return lengths, links, prices, locations, brokers, sale_pending_fields

    @staticmethod
    def get_price_and_status_lists(price):
        # timestamp the crawl
        today = TimeManager.get_todays_date().isoformat()
        price_list = [(price, today)]
        status_list = [('active', today)]

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
    def get_hours(description):
        # search for hours
        words_for_hour = {'hour', 'time', 'stunde', 'ora', 'heure', 'uur', 'tunnin', 'timme', 'saat', 'hora'}

        if any(word in description for word in words_for_hour):
            # add details to item info
            hours = 'hour in description'
        else:
            hours = 'no hour info'

        return hours

