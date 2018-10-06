# -*- coding: utf-8 -*-
# packages
import scrapy
from gemi.database import get_client_and_db


class DetailSpider(scrapy.Spider):
    name = 'detail'
    allowed_domains = ['yachtworld.com']
    base_url = 'https://www.yachtworld.com'

    # entry point
    def __init__(self, *args, **kwargs):
        super(DetailSpider, self).__init__(*args, **kwargs)
        client, db = get_client_and_db()
        self.start_urls = db.yachts.distinct('link')

    # Send urls to parse
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, meta={'url': url}, callback=self.parse)

    def parse(self, response):
        full_spec_selector = 'div.full_specs div:first-child::text'
        full_specs = response.css(full_spec_selector).extract()

        # hour_in_various_languages = {'hour', 'time', 'stunde', 'ora', 'heure', 'uur', 'tunnin', 'timme', 'saat',   'hora'}

        specs = dict()
        self.logger.info(full_specs)

        for line in full_specs:
            line = " ".join(line.split()).lower()
            line = line.split(':')
            self.logger.info(line)
            spec_key = line[0]
            spec_value = line[1]
            specs[spec_key] = spec_value

        yield specs
