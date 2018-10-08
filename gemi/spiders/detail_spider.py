# -*- coding: utf-8 -*-
# packages
import scrapy
from gemi.database import db


class DetailSpider(scrapy.Spider):
    name = 'detail'
    domain = 'yachtworld.com'
    base_url = 'https://www.yachtworld.com'
    allowed_domains = [domain]

    # entry point
    def __init__(self, *args, **kwargs):
        super(DetailSpider, self).__init__(*args, **kwargs)
        self.start_urls = db.yachts.distinct('link')

    # Send urls to parse
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, meta={'url': url}, callback=self.parse)

    def parse(self, response):
        full_spec_selector = 'div.fullspecs div:first-child::text'
        full_specs = response.css(full_spec_selector).extract()
        item_link = response.meta['url']

        specs = dict()
        for line in full_specs:
            line = " ".join(line.split()).lower()
            line = line.split(':')
            if len(line) == 2:
                spec_key = " ".join(line[0].split())
                spec_value = " ".join(line[1].split())
                specs[spec_key] = spec_value
            else:
                continue

        db.update(
            {'link': item_link},
            {
                '$set':
                    {
                        'details': specs
                    }
            }
        )

        yield None
