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
        prices = processor.remove_empty_prices(prices)

        locations = page.css(self.location_selector).extract()
        brokers = page.css(self.broker_selector).extract()
        sale_pending_fields = page.css(self.sale_pending).extract()

        return lengths, links, prices, locations, brokers, sale_pending_fields
