# -*- coding: utf-8 -*-
import scrapy
# util
from urllib.parse import urlencode
from collections import OrderedDict
# db
from gemi.database import get_db_client
# time
import time
import datetime


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

        # basics
        self.base_url = 'https://www.yachtworld.com'
        self.base_query_parameters = dict()
        self.root_search_url = 'https://www.yachtworld.com/core/listing/cache/searchResults.jsp'

        # control knobs
        self.next_page = next_page  # follow to the next pages
        self.should_get_details = details  # parse details page

        # init db
        self.client = get_db_client()
        self.db = self.client['gemi']  # db name

        # get links seen
        self.links_seen = self.db.yachts.distinct('link')

        self.start_urls, self.days = self.generate_base_query_urls()

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
            'ps': 200  # entries per page
        }

        within_x_days = [(1, 1535580789155), (3, 1535407989155), (7, 1535062389155),
                         (14, 1534457589155), (30, 1533075189155), (60, 1530483189155), ('60+', '')]

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

    @staticmethod
    def check_price_change(item, price):
        if item['price'][-1][0] != price:  # get the value of the last price (price,time) tuples
            timestamp = time.time()
            new_price = (price, timestamp)
            item['price'].append(new_price)
        return item

    def parse(self, response):
        # table selectors
        search_results_table_selector = 'div#searchResultsDetailsABTest'
        # field selectors
        link_selector = 'div.make-model a::attr(href)'
        length_selector = 'div.make-model a span.length::text'
        price_selector = 'div.price::text'
        location_selector = 'div.location::text'
        broker_selector = 'div.broker::text'

        # define the data to process
        search_results = response.css(search_results_table_selector)

        # result_count_selector = 'div.searchResultsCount--mobile-container__searchResultsCount'
        # result_count = response.css(result_count_selector).extract()

        try:
            days_on_market = response.meta['days-on-market']
        except KeyError:
            days_on_market = 'unknown'

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

                # track earlier items
                if link in self.links_seen:
                    # get the item
                    item = self.db.yachts.find_one({"link": link})
                    item = self.check_price_change(item, price)
                    # increment days on market
                    item['days_on_market'] += 1

                    self.db.test.find_one_and_replace({'link': link}, item)

                    continue

                # if seen first time
                self.links_seen.add(link)
                link_to_the_item_details, basic_fields = self.get_basic_fields(length, link, price, location, broker)
                basic_fields['days_on_market'] = days_on_market

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

    def get_basic_fields(self, length, link, price, location, broker):
        # make the link work
        link_to_the_item_details = self.base_url + link

        # get the year and model from the link
        split_link = link.split('/')
        year, model = split_link[2], split_link[3]

        # clean the fields
        cleaned_fields = list(map(lambda field: " ".join(field.split()), [price, length, location, broker]))
        price, length, location, broker = cleaned_fields

        price = price.replace('US$', '')

        # timestamp the crawl
        timestamp = time.time()
        # current_time = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        price = [(price, timestamp)]
        status = [('active', timestamp)]


        basic_fields = {
            'model': model,
            'year': year,
            'length': length,
            'price': price,
            'location': location,
            'broker': broker,
            'link': link_to_the_item_details,
            'status': status
        }
        return link_to_the_item_details, basic_fields

    @staticmethod
    def parse_details(response, page):
        detail_selector = 'div.boatdetails::text'
        full_spec_selector = 'div.fullspecs::text'

        # parse fields
        details = page.css(detail_selector).extract()
        full_specs = page.css(full_spec_selector).extract()

        # add details to the basic fields dict
        response.meta['full_specs'] = full_specs
        response.meta['details'] = details

        # send the item info to the pipeline
        yield response.meta


class GemiUtil(object):

    @staticmethod
    def remove_empty_prices(prices):
        for i, price in enumerate(prices):
            clean_price = price.replace('\n', '').strip()
            if clean_price == '':
                prices.pop(i)
        return prices
