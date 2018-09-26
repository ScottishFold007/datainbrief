from gemi.data_engine.util import Cleaner


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
    def get_maker_model_and_year(sub_link):
        # get the year and model from the link
        split_link = sub_link.split('/')
        year, maker_and_model = split_link[2], split_link[3]
        parts = maker_and_model.split('-')
        maker = parts[0]
        model = " ".join(parts[1:-1])
        return maker, model, year

    @staticmethod
    def extract_city_state_and_country_from_location(location):
        state = ""

        location_parts = location.split(',')

        country = location_parts[-1]
        city = location_parts[0]

        if len(location_parts) == 3:
            state = location_parts[2]

        return city, state, country


