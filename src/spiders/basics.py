from scrapy import Request
from src.spiders.base import BaseSpider
from src.helpers.url_generator import url_generator
from src.helpers.FieldExtractor import FieldExtractor
from enum import Enum


class Constants(Enum):
    search_results_table_selector = '// *[ @ id = "searchResultsDetailsABTest"]/div'
    next_page_button_selector = 'div.searchResultsNav span.navNext a.navNext::attr(href)'
    days = 'days_on_market'
    link = 'link'


class BasicSpider(BaseSpider):
    name = 'basics'

    custom_settings = {
        'ITEM_PIPELINES': {
            'src.pipelines.BasicPipeline': 200,
        }
    }

    # entry point
    def __init__(self, *args, **kwargs):
        super(BasicSpider, self).__init__(*args, **kwargs)
        self.field_extractor = FieldExtractor()
        self.next_page = True

    # Send urls to parse
    def start_requests(self):
        for day, url in url_generator():
            yield Request(url=url, meta={Constants.days: day}, callback=self.parse)

    def parse(self, response):
        # define the data to process
        search_results_table = response.xpath(Constants.search_results_table_selector)
        for row in search_results_table:
            item = self.field_extractor.extract_item(row)
            if item[Constants.link] == '':
                continue
            item[Constants.days] = response.meta[Constants.days]
            yield item

        # follow to the next page
        if self.next_page:
            next_page_href = response.css(Constants.next_page_button_selector).extract_first()
            if next_page_href is not None:
                next_page_url = self.base_url + next_page_href
                yield response.follow(next_page_url, meta=response.meta, callback=self.parse)
