# -*- coding: utf-8 -*-
import scrapy
# util
from urllib.parse import urlencode
from collections import OrderedDict
from gemi.util import GemiUtil
# db
from gemi.database import Database
# processor
from gemi.processor import FieldProcessor


class GemiSpider(scrapy.Spider):
    name = 'gemi'
    allowed_domains = ['yachtworld.com']

    # Configure item pipelines
    # See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
    custom_settings = {
        'ITEM_PIPELINES': {
            # 'gemi.pipelines.DuplicatesPipeline': 200,
            'gemi.pipelines.MongoPipeline': 300  # pipeline with smaller number executed first
        }
    }

    # entry point
    def __init__(self, next_page=True, details=False, *args, **kwargs):
        super(GemiSpider, self).__init__(*args, **kwargs)

        # basics
        self.base_url = 'https://www.yachtworld.com'
        self.base_query_parameters = dict()
        self.root_search_url = 'https://www.yachtworld.com/core/listing/cache/searchResults.jsp'

        # control knobs
        self.next_page = next_page  # follow to the next pages
        self.should_get_details = details  # parse details page

        # init db
        self.client, self.db = Database()

        # get links seen
        self.links_seen = self.db.yachts.distinct('link')

        self.start_urls, self.days = self.generate_base_query_urls()

        # init selectors

        # table selector
        self.search_results_table_selector = 'div#searchResultsDetailsABTest'
        # basic field selectors
        self.link_selector = 'div.make-model a::attr(href)'
        self.length_selector = 'div.make-model a span.length::text'
        self.price_selector = 'div.price::text'
        self.location_selector = 'div.location::text'
        self.broker_selector = 'div.broker::text'
        # details
        self.detail_selector = 'div.boatdetails::text'
        self.full_spec_selector = 'div.fullspecs::text'
        # next page link
        self.next_page_button_selector = 'div.searchResultsNav span.navNext a.navNext::attr(href)'

    # query generator
    def generate_base_query_urls(self):
        urls = list()
        days = list()

        # default query
        self.base_query_parameters = {
            'fromLength': 25,
            'toLength': '',
            'fromYear': 1995,
            'toYear': '',
            'fromPrice': 20000,
            'toPrice': 8000000,
            'luom': 126,  # units feet, meter=127
            'currencyid': 100,  # US dollar
            'ps': 300  # entries per page
        }

        within_x_days = [(1, 1535580789155), (3, 1535407989155), (7, 1535062389155),
                         (14, 1534457589155), (30, 1533075189155), (60, 1530483189155), (100, '')]

        within_x_days = OrderedDict(within_x_days)

        # generate queries for all day options
        for day, pbsint in within_x_days.items():
            self.base_query_parameters['pbsint'] = pbsint
            query_string = urlencode(self.base_query_parameters, 'utf-8')
            query_url = self.root_search_url + '?' + query_string
            urls.append(query_url)
            days.append(day)

        return urls, days

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
        prices = GemiUtil.remove_empty_prices(prices)

        locations = page.css(self.location_selector).extract()
        brokers = page.css(self.broker_selector).extract()

        return lengths, links, prices, locations, brokers

    def update_item_info(self, link, price):
        # get the item
        item = self.db.yachts.find_one({"link": link})
        # check the price
        item = GemiUtil.check_price_change(item, price)
        # increment days on market
        item['days_on_market'] += 7
        # update only changed fields
        self.db.test.find_one_and_replace({'link': link}, item)

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
            lengths, links, prices, locations, brokers = self.extract_fields(page)

            basic_fields = dict()
            basic_fields['days_on_market'] = days_on_market

            for length, link, price, location, broker in zip(lengths, links, prices, locations, brokers):

                # track earlier items
                if link in self.links_seen:
                    self.update_item_info(link, price)
                    continue

                # if seen first time
                self.links_seen.add(link)

                # clean
                price, length, location, broker = FieldProcessor.clean_basic_fields(price, length, location, broker)

                # fill in the item info
                item_info = {
                    'length': length,
                    'location': location,
                    'broker': broker,
                    'link': link
                }
                basic_fields.update(item_info)

                # add model and year
                model_and_year = FieldProcessor.get_model_and_year(link)
                basic_fields.update(model_and_year)

                # add price and status
                price_and_status = FieldProcessor.get_price_and_status_lists(price)
                basic_fields.update(price_and_status)

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
            self.follow_to_the_next_page(response)

    def parse_details(self, response, page):
        # parse fields
        details = page.css(self.detail_selector).extract()
        full_specs = page.css(self.full_spec_selector).extract()

        # search for hours
        hours = GemiUtil.extract_hours_from_details(details)

        # add details to the basic fields dict
        response.meta['full_specs'] = full_specs
        response.meta['details'] = details
        response.meta['hours'] = hours

        # send the item info to the pipeline
        yield response.meta

    def follow_to_the_next_page(self, response):
        next_page_href = response.css(self.next_page_button_selector).extract_first()
        if next_page_href is not None:
            next_page_url = self.base_url + next_page_href
            yield response.follow(next_page_url, meta=response.meta, callback=self.parse)
