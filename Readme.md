
## YachtBuyer
crawl boats, 

process and clean data,

save it to a separate, remote Mongodb server 

### Deploy 
https://app.scrapinghub.com/p/344868/deploy

for general reference https://docs.scrapy.org/en/latest/topics/deploy.html

### IP Rotation
Just enable Crawlera from settings and set the API key. 

## Data Processing 
spiders get the raw data from the page 
and send them to processors in data_engine

processors clean data, track changes and save data. 

### Item Model 
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

## Database
https://api.mongodb.com/python/current/tutorial.html

### grouping and stats
https://docs.mongodb.com/manual/reference/operator/aggregation/

http://api.mongodb.com/python/current/examples/aggregation.html