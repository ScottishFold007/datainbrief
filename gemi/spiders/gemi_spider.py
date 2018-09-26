# -*- coding: utf-8 -*-
# packages
import scrapy
# self coded modules
from gemi.data_engine.item_processor import ItemProcessor
from gemi.data_engine.field_extractor import FieldExtractor
from gemi.data_engine.util import QueryGenerator


class GemiSpider(scrapy.Spider):
    name = 'gemi'
    allowed_domains = ['yachtworld.com']
    base_url = 'https://www.yachtworld.com'

    # entry point
    def __init__(self, next_page=True, *args, **kwargs):
        super(GemiSpider, self).__init__(*args, **kwargs)
        self.next_page = next_page  # follow to the next pages
        # get urls
        self.start_urls = QueryGenerator.generate_urls_for_search_queries()
        self.extractor = FieldExtractor()
        self.processor = ItemProcessor()

    # Send urls to parse
    def start_requests(self):
        days = [1, 3, 7, 14, 30, 60, '60+']
        for url, day in zip(self.start_urls, days):
            yield scrapy.Request(url=url, meta={'days-on-market': day}, callback=self.parse)

    def parse(self, response):
        # define the data to process
        search_results_table_selector = 'div#searchResultsDetailsABTest'
        search_results_table = response.css(search_results_table_selector)
        days_on_market = response.meta['days-on-market']

        for page in search_results_table:
            lengths, links, prices, locations, brokers, sale_pending_fields = self.extractor.extract_fields(page)

            for length, link, price, location, broker, sale_pending in zip(lengths, links, prices,
                                                                           locations, brokers,
                                                                           sale_pending_fields):

                item_data = [length, link, price, location, broker, sale_pending, days_on_market]
                self.processor.update_and_save_item_data(item_data)

                yield None

        # follow to the next page
        if self.next_page:
            next_page_button_selector = 'div.searchResultsNav span.navNext a.navNext::attr(href)'
            next_page_href = response.css(next_page_button_selector).extract_first()
            if next_page_href is not None:
                next_page_url = self.base_url + next_page_href
                yield response.follow(next_page_url, meta=response.meta, callback=self.parse)
