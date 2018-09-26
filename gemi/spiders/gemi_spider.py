# -*- coding: utf-8 -*-
# packages
import scrapy
# self coded modules
from gemi.data_engine.basic_processor import ItemProcessor
from gemi.data_engine.extractor import FieldExtractor
from gemi.data_engine.util import QueryGenerator
from gemi.data_engine.database import get_db



class GemiSpider(scrapy.Spider):
    name = 'gemi'
    allowed_domains = ['yachtworld.com']

    # Configure item pipelines
    # See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
    custom_settings = {
        'ITEM_PIPELINES': {
            # 'gemi.pipelines.DuplicatesPipeline': 200,
            'gemi.pipelines.NewItemPipeline': 300  # pipeline with smaller number executed first
        }
    }

    # entry point
    def __init__(self, next_page=True, *args, **kwargs):
        super(GemiSpider, self).__init__(*args, **kwargs)
        self.base_url = 'https://www.yachtworld.com'
        self.next_page = next_page  # follow to the next pages
        # get urls
        self.start_urls = QueryGenerator.generate_urls_for_search_queries()
        self.extractor = FieldExtractor()
        self.processor = ItemProcessor()
        # init db
        self.db = get_db()
        # get links seen
        self.set_initial_status()

    def set_initial_status(self):
        # set all as not updated first
        self.db.yachts.update_many(
            {},  # select unsold items
            {
                '$set': {'status.updated': False}
            }
        )

    # Send urls to parse
    def start_requests(self):
        days = [1, 3, 7, 14, 30, 60, 100]
        for url, day in zip(self.start_urls, days):
            yield scrapy.Request(url=url, meta={'days-on-market': day}, callback=self.parse)

    def parse(self, response):
        # define the data to process
        search_results_table_selector = 'div#searchResultsDetailsABTest'
        search_results = response.css(search_results_table_selector)

        try:
            days_on_market = response.meta['days-on-market']
        except KeyError:
            days_on_market = 'unknown'

        for page in search_results:
            lengths, links, prices, locations, brokers, sale_pending_fields = self.extractor.extract_fields(page)

            item = dict()
            item['days_on_market'] = days_on_market

            for length, link, price, location, broker, sale_pending in zip(lengths, links, prices,
                                                                           locations, brokers,
                                                                           sale_pending_fields):

                new_item = self.processor.update_item(length, link, price, location,
                                                      broker, sale_pending, item)
                if not new_item:
                    # just updated already existing item
                    continue

                # send the item to the pipeline
                yield new_item

        # follow to the next page
        if self.next_page:
            next_page_button_selector = 'div.searchResultsNav span.navNext a.navNext::attr(href)'
            next_page_href = response.css(next_page_button_selector).extract_first()
            if next_page_href is not None:
                next_page_url = self.base_url + next_page_href
                yield response.follow(next_page_url, meta=response.meta, callback=self.parse)
