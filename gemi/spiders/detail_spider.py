# -*- coding: utf-8 -*-
# packages
import scrapy
import gemi.data_engine.detail_processor as processor
from gemi.database import get_client_and_db


class DetailSpider(scrapy.Spider):
    name = 'detail'
    allowed_domains = ['yachtworld.com']
    client, db = get_client_and_db()
    base_url = 'https://www.yachtworld.com'

    custom_settings = {
        'ITEM_PIPELINES': {
            'gemi.pipelines.DetailPipeline': 300  # pipeline with smaller number executed first
        }
    }

    # entry point
    def __init__(self, *args, **kwargs):
        super(DetailSpider, self).__init__(*args, **kwargs)
        self.start_urls = self.get_detail_links()

    def get_detail_links(self):
        links = self.db.yachts.distinct('link')
        urls = list()
        for link in links:
            if 'http' in link:  # already ok
                continue
            url = self.base_url + link
            urls.append(url)
        return urls

    # Send urls to parse
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        detail_selector = 'div.boatdetails::text'
        detail = response.css(detail_selector).extract()
        hours = processor.get_hours(detail)
        item = dict()
        item.update({'hours': hours})
        if hours == 'hour in description':
            detail = " ".join(detail.split())
            item.update({'detail': detail})
        # send the item info to the pipeline
        yield item
