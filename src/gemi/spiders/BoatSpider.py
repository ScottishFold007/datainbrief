from gemi.BaseClasses.BaseSpider import AbstractSpider
from scrapy import Request
from gemi.util.URLGenerator import URLManager
from gemi.util.DataFieldExtractor import DataFieldExtractor


class BoatSpider(AbstractSpider):
    name = 'boats'
    start_urls = list()
    base_url = 'https://www.yachtworld.com'
    allowed_domains = ['yachtworld.com']
    next_page = True

    custom_settings = {
        'ITEM_PIPELINES': {
            'gemi.pipelines.GemiPipeline': 200,
        }
    }

    # entry point
    def __init__(self, *args, **kwargs):
        super(BoatSpider, self).__init__(*args, **kwargs)
        self.url_manager = URLManager()
        self.data_field_extractor = DataFieldExtractor()

    # Send urls to parse
    def start_requests(self):
        for day, url in self.url_manager.url_generator():
            yield Request(url=url, meta={'days_on_market': day}, callback=self.parse)

    def parse(self, response):
        # define the data to process
        search_results_table_selector = '// *[ @ id = "searchResultsDetailsABTest"]/div'
        search_results_table = response.xpath(search_results_table_selector)
        for row in search_results_table:
            item = self.data_field_extractor.extract_item(row)
            if item['link'] == '':
                continue
            item['days_on_market'] = response.meta['days_on_market']
            yield item

        # follow to the next page
        if self.next_page:
            next_page_button_selector = 'div.searchResultsNav span.navNext a.navNext::attr(href)'
            next_page_href = response.css(next_page_button_selector).extract_first()
            if next_page_href is not None:
                next_page_url = self.base_url + next_page_href
                yield response.follow(next_page_url, meta=response.meta, callback=self.parse)

