# -*- coding: utf-8 -*-
# packages
import scrapy
# self coded modules
# db
from gemi.database import get_db
# processor
import gemi.processor as processor


class GemiSpider(scrapy.Spider):
    name = 'gemi'
    allowed_domains = ['yachtworld.com']

    # init selectors
    # table selector
    search_results_table_selector = 'div#searchResultsDetailsABTest'
    # basic field selectors
    link_selector = 'div.make-model a::attr(href)'
    length_selector = 'div.make-model a span.length::text'
    price_selector = 'div.price::text'
    location_selector = 'div.location::text'
    sale_pending = 'div.location span.active_field'
    broker_selector = 'div.broker::text'
    # details
    detail_selector = 'div.boatdetails::text'
    full_spec_selector = 'div.fullspecs::text'
    # next page link
    next_page_button_selector = 'div.searchResultsNav span.navNext a.navNext::attr(href)'

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
        # init db
        self.db = get_db()
        # get links seen
        self.links_seen = self.db.yachts.distinct('link')
        self.set_initial_status()
        # get urls
        self.start_urls, self.days = processor.generate_base_query_urls()

    def set_initial_status(self):
        # set all as not updated first
        self.db.yachts.update_many(
            {},  # select all
            {
                '$set': {'updated': False}
            }
        )

    # Send urls to parse
    def start_requests(self):
        for url, day in zip(self.start_urls, self.days):
            yield scrapy.Request(url=url, meta={'days-on-market': day}, callback=self.parse)

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

    def update_item_info(self, link, price, sale_pending):
        # get the item
        item = self.db.yachts.find_one({"link": link})
        # check the price
        price_list = processor.check_price_change(item, price)
        # check status
        sale_status = processor.check_status_change(item, sale_pending)

        # update only changed fields
        self.db.yachts.find_one_and_update(
            {'link': link},  # filter
            {
                '$unset': {'price': ""},  # remove price field
                '$set': {'price_list': price_list, 'sale_status': sale_status, 'updated': True},
                '$inc': {'days_on_market': 7}
            }
        )

    def parse(self, response):
        # define the data to process
        search_results = response.css(self.search_results_table_selector)
        # result_count_selector = 'div.searchResultsCount--mobile-container__searchResultsCount'
        # result_count = response.css(result_count_selector).extract()

        try:
            days_on_market = response.meta['days-on-market']
        except KeyError:
            days_on_market = 'unknown'

        for page in search_results:
            lengths, links, prices, locations, brokers, sale_pending_fields = self.extract_fields(page)

            item_info = dict()
            item_info['days_on_market'] = days_on_market

            for length, link, price, location, broker, sale_pending in zip(lengths, links, prices,
                                                                           locations, brokers,
                                                                           sale_pending_fields):


                # track earlier items
                if link in self.links_seen:
                    # self.update_item_info(link, price, sale_pending)
                    continue

                # if seen first time
                self.links_seen.append(link)

                # clean
                price, length, location, broker = processor.clean_basic_fields(price, length, location, broker)

                # fill in the item info
                basic_fields = {
                    'length': length,
                    'location': location,
                    'broker': broker,
                    'link': link,
                    'updated': True,
                    'removed': False
                }
                item_info.update(basic_fields)

                # add model and year
                model_and_year = processor.get_model_and_year(link)
                item_info.update(model_and_year)

                # add price and status
                price_and_status = processor.get_price_and_status_lists(price)
                item_info.update(price_and_status)

                # go to the item page to get details
                if self.should_get_details:
                    link_to_the_item_details = self.base_url + link
                    # send a request to the details page
                    yield scrapy.Request(
                        link_to_the_item_details,
                        callback=self.parse_details(page=page),
                        meta=basic_fields
                    )
                else:
                    # send the item to the pipeline
                    yield basic_fields

        # follow to the next page
        if self.next_page:
            next_page_href = response.css(self.next_page_button_selector).extract_first()
            if next_page_href is not None:
                next_page_url = self.base_url + next_page_href
                yield response.follow(next_page_url, meta=response.meta, callback=self.parse)

    def parse_details(self, response, page):
        item_info = response.meta

        # parse fields
        details = page.css(self.detail_selector).extract()
        full_specs = page.css(self.full_spec_selector).extract()

        # search for hours
        hours = processor.extract_hours_from_details(details)

        # add details to item info
        details = {'full_specs': full_specs,
                   'details': details,
                   'hours': hours}
        item_info.update(details)

        # send the item info to the pipeline
        yield item_info

    def follow_to_the_next_page(self, response):
        pass
