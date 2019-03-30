from pymongo import MongoClient
from src.BaseClasses.BaseDB import BaseDB
from src.helpers.date_time import todays_date, date_of_x_days_ago


class BoatsDatabase(BaseDB):
    client = MongoClient(host='mongodb://<dbuser>:<dbpassword>@ds237072.mlab.com:37072/src',
                         port=47450,
                         username='roxy',
                         password='gemicik1',
                         authSource='src',
                         authMechanism='SCRAM-SHA-1')

    db_name = 'src'
    db = client[db_name]
    collection_name = 'boats'

    def __init__(self):
        super(BaseDB, self).__init__()

    @classmethod
    def get_items_without_details(cls):
        return cls.db[cls.collection_name].distinct('link', {'details': {'$exists': False}})

    def save_updated_item(self, link, updates):
        # update only changed fields
        self.db[self.collection_name].find_one_and_update(
            {'link': link},  # filter
            {
                '$set': updates,
                '$inc': {'days_on_market': 1}
            }
        )

    def save_details(self, link, details):
        self.db[self.collection_name].update_one(
            {'link': link},
            {
                '$set':
                    {
                        'details': details
                    }
            }
        )

    def check_removed_items(self):
        # set all as not updated first
        date_of_yesterday = date_of_x_days_ago(2)

        self.db[self.collection_name].update_many(
            {"dates.last_seen": {"$lt": date_of_yesterday}},
            {
                '$set': {
                    'status.removed': True,
                    'dates.removed': todays_date
                }
            }
        )
