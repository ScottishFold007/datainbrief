from pymongo.errors import DuplicateKeyError
from abc import ABC, abstractmethod


class AbstractDatabase(ABC):
    client = ''
    db_name = ''
    db = ''
    collection_name = ''


class BaseDB(AbstractDatabase):
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
    def save_new_item(cls, item):
        try:
            # write new item to the db
            cls.db[cls.collection_name].insert_one(item)
        except DuplicateKeyError:
            print('duplicate item')

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
