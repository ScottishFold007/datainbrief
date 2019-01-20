from pymongo import MongoClient
from gemi.BaseClasses.BaseDB import BaseDB
from gemi.helpers.date_time import todays_date, date_of_x_days_ago
import re
from tqdm import tqdm
from pymongo.errors import CursorNotFound, DuplicateKeyError


class BoatsDatabase(BaseDB):
    client = MongoClient(host='mongodb://<dbuser>:<dbpassword>@ds237072.mlab.com:37072/gemi',
                         port=47450,
                         username='roxy',
                         password='gemicik1',
                         authSource='gemi',
                         authMechanism='SCRAM-SHA-1')

    db_name = 'gemi'
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


def x():
    cursor = boats_database.db.boats.find({'maker': {"$exists": True}})
    print(cursor.count())
    try:
        for doc in tqdm(cursor):
            boats_database.db.boats.find_one_and_update(
                {'link': doc['link']},
                {
                    '$set': {
                        'model': (doc['maker'] + ' ' + doc['model']).lower(),
                        'length': int(re.findall('\d+', doc['length'])[0]),

                    },
                    '$unset': {'maker': ""}
                }
            )
    except CursorNotFound:
        x()


def y():
    cursor = boats_database.db.boats.find({'details.engine_hours': {"$exists": True}})
    print(cursor.count())
    count = 0
    for doc in tqdm(cursor):
        try:
            hours = doc['details']['engine_hours']
            if isinstance(hours, int):
                count += 1
                print(count)
                pass
            else:
                boats_database.db.boats.find_one_and_update(
                    {'link': doc['link']},
                    {
                        '$set': {
                            'details.engine_hours': int(hours)
                        }
                    }
                )
        except CursorNotFound:
            y()
        except ValueError as e:
            continue


boats_database = BoatsDatabase()



def lowercase_model_fix_links():
    cursor = boats_database.db.boats.find()
    base_url = 'https://www.yachtworld.com'
    for doc in cursor:
        updates = dict()
        link = doc["link"]
        if 'http' not in link:
            updates["link"] = base_url + link

        updates["model"] = doc["model"].lowercase() 
        boats_database.save_updated_item

        try:
            boats_database.db.boats.find_one_and_update(
                {'link': link}, 
                {
                    '$set': updates,
                }
            )
        except DuplicateKeyError:
            


if __name__ == "__main__":
    '''
    lowercase
    http links -> if same -> ? 


    '''



       



