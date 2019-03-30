from pymongo import MongoClient
from src.helpers.date_time import todays_date, date_of_x_days_ago
from pymongo.errors import DuplicateKeyError


class BoatsDatabase(object):
    client = MongoClient(host='mongodb://<dbuser>:<dbpassword>@ds237072.mlab.com:37072/src',
                         port=47450,
                         username='roxy',
                         password='gemicik1',
                         authSource='src',
                         authMechanism='SCRAM-SHA-1')

    db_name = 'src'
    db = client[db_name]
    collection_name = 'boats'

    @classmethod
    def save_new_item(cls, item):
        try:
            # write new item to the db
            cls.db[cls.collection_name].insert_one(item)
        except DuplicateKeyError:
            print('duplicate item')

    @classmethod
    def update_item(cls, link, updates):
        # update only changed fields
        cls.db[cls.collection_name].find_one_and_update(
            {'link': link},  # filter
            {
                '$set': updates,
                '$inc': {'days_on_market': 1}
            }
        )

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

    @classmethod
    def rename_field(cls, old_name, new_name):
        cls.db[cls.collection_name].update_many({}, {'$rename': {old_name: new_name}})
        print('renamed %s to %s' % (old_name, new_name))

    # Remove multiple fields
    @classmethod
    def remove_field(cls, field_name):
        cls.db[cls.collection_name].update(
            {},
            {
                '$unset': {field_name: ""}
            },
            multi=True
        )
        print('removed field %s' % field_name)

    @classmethod
    def get_a_single_item_by_key(cls, key_string, key):
        return cls.db[cls.collection_name].find_one({key_string: key})

    @classmethod
    def get_distinct_items_by_key(cls, key_string):
        return cls.db[cls.collection_name].distinct(key_string)

    @classmethod
    def get_distinct_links(cls):
        return cls.db[cls.collection_name].distinct("link")

    @classmethod
    def add_a_new_field(cls, field_name, field_data):
        cls.db[cls.collection_name].find(
            {
                field_name: {"$exists": False},
            },
            {
                '$set': {field_name: field_data}
            }
        )

    @classmethod
    def delete_if_a_field_does_not_exist(cls, field_name):
        cls.db[cls.collection_name].delete_many({field_name: {"$exists": False}})
