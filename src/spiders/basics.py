from scrapy import Request
from src.spiders.base import BaseSpider
from src.helpers.url_generator import url_generator
from src.helpers.FieldExtractor import FieldExtractor


class BasicSpider(BaseSpider):
    name = 'basics'

    custom_settings = {
        'ITEM_PIPELINES': {
            'src.helpers.pipelines.BasicPipeline': 200,
        }
    }

    search_results_table_selector = '// *[ @ id = "searchResultsDetailsABTest"]/div'
    next_page_button_selector = 'div.searchResultsNav span.navNext a.navNext::attr(href)'

    # entry point
    def __init__(self, *args, **kwargs):
        super(BasicSpider, self).__init__(*args, **kwargs)
        self.field_extractor = FieldExtractor()
        self.next_page = True

    # Send urls to parse
    def start_requests(self):
        for day, url in url_generator():
            yield Request(url=url, meta={'days_on_market': day}, callback=self.parse)

    def parse(self, response):
        # define the data to process
        search_results_table = response.xpath(self.search_results_table_selector)
        for row in search_results_table:
            item = self.field_extractor.extract_item(row)
            if item['link'] == '':
                continue
            item['days_on_market'] = response.meta['days_on_market']
            yield item

        # follow to the next page
        if self.next_page:
            next_page_href = response.css(self.next_page_button_selector).extract_first()
            if next_page_href is not None:
                next_page_url = self.base_url + next_page_href
                yield response.follow(next_page_url, meta=response.meta, callback=self.parse)
