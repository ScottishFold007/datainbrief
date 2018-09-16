# -*- coding: utf-8 -*-
# packages
import scrapy
# self coded modules
from gemi.processor import ItemProcessor
from gemi.extractor import FieldExtractor


class GemiSpider(scrapy.Spider):
    name = 'gemi'
    allowed_domains = ['yachtworld.com']

    # Configure item pipelines
    # See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
    custom_settings = {
        'ITEM_PIPELINES': {
            'gemi.pipelines.DuplicatesPipeline': 200,
            'gemi.pipelines.MongoPipeline': 300  # pipeline with smaller number executed first
        }
    }

    # entry point
    def __init__(self, next_page=True, details=False, *args, **kwargs):
        super(GemiSpider, self).__init__(*args, **kwargs)
        self.base_url = 'https://www.yachtworld.com'
        # control knobs
        self.next_page = next_page  # follow to the next pages
        self.should_get_details = details  # parse details page
        # get urls
        self.start_urls, self.days = processor.generate_base_query_urls()
        self.extractor = FieldExtractor()
        self.processor = ItemProcessor()

    # Send urls to parse
    def start_requests(self):
        for url, day in zip(self.start_urls, self.days):
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

            item_info = dict()
            item_info['days_on_market'] = days_on_market

            for length, link, price, location, broker, sale_pending in zip(lengths, links, prices,
                                                                           locations, brokers,
                                                                           sale_pending_fields):

                item_info = ItemProcessor.process_item_info(length, link, price, location, broker, sale_pending,
                                                            item_info)
                if not item_info:  # just updated already existing item
                    # continue
                    pass

                # go to the item page to get details
                if self.should_get_details:
                    link_to_the_item_details = self.base_url + link
                    # send a request to the details page
                    yield scrapy.Request(
                        link_to_the_item_details,
                        callback=self.parse_details,
                        meta=item_info
                    )
                else:
                    # send the item to the pipeline
                    yield item_info

        # follow to the next page
        if self.next_page:
            next_page_button_selector = 'div.searchResultsNav span.navNext a.navNext::attr(href)'
            next_page_href = response.css(next_page_button_selector).extract_first()
            if next_page_href is not None:
                next_page_url = self.base_url + next_page_href
                yield response.follow(next_page_url, meta=response.meta, callback=self.parse)

    @staticmethod
    def parse_details(response):
        item_info = response.meta

        detail_selector = 'div.boatdetails::text'
        description = response.css(detail_selector).extract()

        # search for hours
        words_for_hour = {'hour', 'time', 'stunde', 'ora', 'heure', 'uur', 'tunnin', 'timme', 'saat', 'hora'}

        if any(word in description for word in words_for_hour):
            # add details to item info
            description = {
                'description': description,
            }
            item_info.update(description)

        # send the item info to the pipeline
        yield item_info
