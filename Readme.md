### Data Model 
a boat is defined as follows

    {
        'length': length,
        'location': location,
        'city': city,
        'state': state,
        'country': country,
        'broker': broker,
        'link': link,
        'status': {
            'active': True,
            'updated': True,
            'removed': False,
            'sold': False,
            'sale-pending': False,
            'price-changed': False
        },
        'dates': {
            'crawled': self.todays_date,
            'last-updated': self.todays_date
        },
        'price': price,
        'maker': maker,
        'model': model,
        'year': year,
        'days_on_market': days_on_market
    }

