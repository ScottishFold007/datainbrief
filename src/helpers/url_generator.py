from urllib.parse import urlencode
from collections import OrderedDict


def url_generator():
    root_search_url = 'https://www.yachtworld.com/core/listing/cache/searchResults.jsp'

    base_query_parameters = {
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

    recent_days_in_seconds = [(1, 1535580789155),
                              (3, 1535407989155),
                              (7, 1535062389155),
                              (14, 1534457589155),
                              (30, 1533075189155),
                              (60, 1530483189155),
                              (90, '')
                              ]

    ordered_recent_days_in_seconds = OrderedDict(recent_days_in_seconds)

    # generate queries for all day options
    for day, pbsint in ordered_recent_days_in_seconds.items():
        base_query_parameters['pbsint'] = pbsint
        query_string = urlencode(base_query_parameters, 'utf-8')
        query_url = root_search_url + '?' + query_string
        yield day, query_url
