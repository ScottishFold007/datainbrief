# -*- coding: utf-8 -*-
import scrapy


class GemiSpider(scrapy.Spider):
    name = 'gemi'
    allowed_domains = ['yachtworld.com']

    # Configure item pipelines
    # See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
    custom_settings = {
        'ITEM_PIPELINES': {
            'gemi.pipelines.MongoPipeline': 300,  # pipeline with smaller number executed first
        }
    }

    def __init__(self, urls, *args, **kwargs):
        super(GemiSpider, self).__init__(*args, **kwargs)
        self.urls = [urls]
        self.base_url = 'https://www.yachtworld.com'

    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        SET_SELECTOR = 'div#searchResultsDetailsABTest'

        ads = response.css(SET_SELECTOR)

        for ad in ads:

            NAME_SELECTOR = 'div.make-model::text'
            LINK_SELECTOR = 'div.image-container a::attr(href)'
            PRICE_SELECTOR = 'div.price::text'
            LOCATION_SELECTOR = 'div.location::text'
            BROKER_SELECTOR = 'div.broker::text'

            names = ad.css(NAME_SELECTOR).extract()
            links = ad.css(LINK_SELECTOR).extract()
            prices = ad.css(PRICE_SELECTOR).extract()
            locations = ad.css(LOCATION_SELECTOR).extract()
            brokers = ad.css(BROKER_SELECTOR).extract()

            # iterate through items
            for name, link, price, location, broker in zip(names, links, prices, locations, brokers):
                link = self.base_url + link
                yield {
                    'title': name.strip(),
                    'link': link,
                    'price': price.replace("\n", " ").strip(),
                    'location': location.replace("\n", " ").strip(),
                    'broker': broker.replace("\n", " ").strip()
                }
