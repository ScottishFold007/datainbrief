from src.util.date_time_ops import date_of_x_days_ago
from pymongo.errors import DuplicateKeyError
from src.db.credentials import db, collection


def save_new_item(item):
    try:
        # write new item to the db
        db[collection].insert_one(item)
    except DuplicateKeyError:
        print('duplicate item')


def get_items_without_details():
    return db[collection].distinct('link', {'details': {'$exists': False}})


def update_and_increment_day(link, updates):
    query = {'link': link}
    command = {'$set': updates, '$inc': {'days_on_market': 1}}
    db[collection].find_one_and_update(query, command)


def update_item(link, updates):
    query = {'link': link}
    command = {'$set': updates}
    db[collection].update_one(query, command)


def check_removed_items():
    # set all as not updated first
    three_days_ago = date_of_x_days_ago(3)
    query = {"dates.last_seen": {"$lt": three_days_ago}}
    command = {'$set': {'status.removed': True, 'dates.removed': three_days_ago}}
    db[collection].update_many(query, command)


def rename_field(old_name, new_name):
    command = {'$rename': {old_name: new_name}}
    db[collection].update_many({}, command)
    print('renamed %s to %s' % (old_name, new_name))


def remove_field(field_name):
    command = {'$unset': {field_name: ""}}
    db[collection].update({}, command, multi=True)
    print('removed field %s' % field_name)


def get_a_single_item_by_key(query):
    return db[collection].find_one(query)


def get_distinct_items_by_key(key_string):
    return db[collection].distinct(key_string)


def add_a_new_field(field_name, field_data):
    query = {field_name: {"$exists": False}}
    update = {'$set': {field_name: field_data}}
    db[collection].find(query, update)


def delete_if_a_field_does_not_exist(field_name):
    query = {field_name: {"$exists": False}}
    db[collection].delete_many(query)
