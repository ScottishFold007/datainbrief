# -*- coding: utf-8 -*-
import scrapy
from urllib.parse import urlencode
from collections import OrderedDict
from itertools import product


class GemiSpider(scrapy.Spider):
    name = 'gemi'
    allowed_domains = ['yachtworld.com']

    # Configure item pipelines
    # See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
    custom_settings = {
        'ITEM_PIPELINES': {
            'gemi.pipelines.DuplicatesPipeline': 200,  # the number in range 0-1000
            'gemi.pipelines.MongoPipeline': 300  # pipeline with smaller number executed first
        }
    }

    # entry point
    def __init__(self, next_page=False, details=False, daily_search=False, *args, **kwargs):
        super(GemiSpider, self).__init__(*args, **kwargs)
        # basics
        self.base_url = 'https://www.yachtworld.com'
        self.base_query_parameters = dict()
        self.root_search_url = 'https://www.yachtworld.com/core/listing/cache/searchResults.jsp'

        # control knobs
        self.next_page = next_page  # follow to the next pages
        self.should_get_details = details  # parse details page
        self.daily_search = daily_search  # search recent day only

    def start_requests(self):
        for url, day in self.generate_base_query_urls():
            yield scrapy.Request(url=url, meta={'days-since-added': day}, callback=self.parse)

    # query generator
    def generate_base_query_urls(self):
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
            'ps': 50  # entries per page
        }

        within_x_days = {1: 1535580789155, 3: 1535407989155, 7: 1535062389155, 14: 1534457589155, 30: 1533075189155,
                         60: 1530483189155}

        if self.daily_search:
            self.base_query_parameters['pbsint'] = within_x_days[1]  # 1 day

        for day, pbsint in within_x_days.items():
            self.base_query_parameters['pbsint'] = pbsint

            query_string = urlencode(self.base_query_parameters, 'utf-8')
            query_url = self.root_search_url + '?' + query_string

            yield query_url, day

    def parse(self, response):
        # table selectors
        search_results_table_selector = 'div#searchResultsDetailsABTest'
        result_count_selector = 'div.searchResultsCount--mobile-container__searchResultsCount'
        # field selectors
        link_selector = 'div.make-model a::attr(href)'
        length_selector = 'div.make-model a span.length::text'
        price_selector = 'div.price::text'
        location_selector = 'div.location::text'
        broker_selector = 'div.broker::text'

        # define the data to process
        search_results = response.css(search_results_table_selector)
        # result_count = response.css(result_count_selector).extract()

        added_since = response.meta['days-since-added']

        for page in search_results:
            # parse fields
            lengths = page.css(length_selector).extract()
            links = page.css(link_selector).extract()
            prices = page.css(price_selector).extract()
            locations = page.css(location_selector).extract()
            brokers = page.css(broker_selector).extract()

            # remove empty prices
            prices = GemiUtil.remove_empty_prices(prices)

            for length, link, price, location, broker in zip(lengths, links, prices, locations, brokers):

                link_to_the_item_details, basic_fields = self.get_basic_fields(length, link, price, location, broker,
                                                                               added_since)

                # go to the item page to get details
                if self.should_get_details:
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
            next_page_href = response.css('div.searchResultsNav span.navNext a.navNext::attr(href)').extract_first()
            if next_page_href is not None:
                next_page_url = self.base_url + next_page_href
                yield response.follow(next_page_url, meta=response.meta, callback=self.parse)

    def get_basic_fields(self, length, link, price, location, broker, added_since):

        # get the year and model from the link
        split_link = link.split('/')
        year, model = split_link[2], split_link[3]

        # clean the fields
        cleaned_fields = list(map(lambda field: " ".join(field.split()), [price, length, location, broker]))
        price, length, location, broker = cleaned_fields

        # make the link work
        link_to_the_item_details = self.base_url + link

        basic_fields = {
            'model': model,
            'year': year,
            'length': length,
            'price': price,
            'location': location,
            'broker': broker,
            'link': link_to_the_item_details,
            'added_since': added_since
        }

        return link_to_the_item_details, basic_fields

    @staticmethod
    def parse_details(response, page):
        detail_selector = 'div.boatdetails::text'
        full_spec_selector = 'div.fullspecs::text'

        # parse fields
        details = page.css(detail_selector).extract()
        full_specs = page.css(full_spec_selector).extract()

        # add field to dict
        response.meta['full_specs'] = full_specs
        response.meta['details'] = details

        # send the item info to the pipeline
        yield response.meta

    def add_extra_query_parameters(self):
        # initialize
        search_urls = list()

        # dynamic query parameters
        hull_materials = {'aluminium': 100, 'composite': 101, 'fiberglass': 102,
                          'steel': 103, 'wood': 104, 'other': 105, 'hypalon': 106,
                          'pvc': 107, 'ferro-cement': 108, 'carbon-fiber': 110}
        fuels = {'gas': 100, 'diesel': 101, 'other': 102}
        number_of_engines = {1: 100, 2: 101, 'other': 102, 'none': 103}
        is_new = [True, False]
        within_x_days = {1: 1535580789155, 3: 1535407989155, 7: 1535062389155, 14: 1534457589155, 30: 1533075189155,
                         60: 1530483189155}

        # generate dynamic queries
        for recent_day, new_or_used, material, fuel, engine_number in product(
                within_x_days, is_new, hull_materials,
                fuels, number_of_engines):
            extra_query_parameters = {'is': new_or_used,
                                      'hmid': material,
                                      'ftid': fuel,
                                      'enid': engine_number,
                                      'pbsint': recent_day
                                      }

            # add new parameters to the search url 
            search_url = urlencode(OrderedDict(data=self.base_query_url, search=extra_query_parameters))

            search_urls.append(search_url)

        return search_urls


class GemiUtil(object):

    @staticmethod
    def remove_empty_prices(prices):
        for i, price in enumerate(prices):
            clean_price = price.replace('\n', '').strip()
            if clean_price == '':
                prices.pop(i)
        return prices
