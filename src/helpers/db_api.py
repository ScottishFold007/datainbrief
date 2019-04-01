from src.util.DateTime import todays_date, date_of_x_days_ago
from pymongo.errors import DuplicateKeyError
from src.helpers.db import db, collection


def save_new_item(item):
    try:
        # write new item to the db
        db[collection].insert_one(item)
    except DuplicateKeyError:
        print('duplicate item')


def update_item(link, updates):
    # update only changed fields
    db[collection].find_one_and_update(
        {'link': link},  # filter
        {
            '$set': updates,
            '$inc': {'days_on_market': 1}
        }
    )


def get_items_without_details():
    return db[collection].distinct('link', {'details': {'$exists': False}})


def save_updated_item(link, updates):
    # update only changed fields
    db[collection].find_one_and_update(
        {'link': link},  # filter
        {
            '$set': updates,
            '$inc': {'days_on_market': 1}
        }
    )


def save_details(link, details, hours):
    db[collection].update_one(
        {'link': link},
        {
            '$set':
                {
                    'details': details,
                    'hours': hours
                }
        }
    )


def check_removed_items():
    # set all as not updated first
    two_days_ago = date_of_x_days_ago(2)

    db[collection].update_many(
        {"dates.last_seen": {"$lt": two_days_ago}},
        {
            '$set': {
                'status.removed': True,
                'dates.removed': todays_date
            }
        }
    )


def rename_field(old_name, new_name):
    db[collection].update_many({}, {'$rename': {old_name: new_name}})
    print('renamed %s to %s' % (old_name, new_name))


# Remove multiple fields

def remove_field(field_name):
    db[collection].update(
        {},
        {
            '$unset': {field_name: ""}
        },
        multi=True
    )
    print('removed field %s' % field_name)


def get_a_single_item_by_key(key_string, key):
    return db[collection].find_one({key_string: key})


def get_distinct_items_by_key(key_string):
    return db[collection].distinct(key_string)


def add_a_new_field(field_name, field_data):
    db[collection].find(
        {
            field_name: {"$exists": False},
        },
        {
            '$set': {field_name: field_data}
        }
    )


def delete_if_a_field_does_not_exist(field_name):
    db[collection].delete_many({field_name: {"$exists": False}})
