
from urllib.parse import urlencode
from collections import OrderedDict


class URLManager(object):
    root_search_url = 'https://www.yachtworld.com/core/listing/cache/searchResults.jsp'

    @staticmethod
    def get_query_parameters():
        # default query
        return {
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

    def url_generator(self):
        base_query_parameters = self.get_query_parameters()

        recent_days_in_seconds = [(60, 1530483189155), (90, ''), (1, 1535580789155), (3, 1535407989155), (7, 1535062389155),
                                  (14, 1534457589155), (30, 1533075189155)]

        ordered_recent_days_in_seconds = OrderedDict(recent_days_in_seconds)

        # generate queries for all day options
        for day, pbsint in ordered_recent_days_in_seconds.items():
            base_query_parameters['pbsint'] = pbsint
            query_string = urlencode(base_query_parameters, 'utf-8')
            query_url = self.root_search_url + '?' + query_string
            yield day, query_url
