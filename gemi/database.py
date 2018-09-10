from pymongo import MongoClient, IndexModel, ASCENDING, DESCENDING, TEXT


class Database(object):
    def __index__(self):
        pass


def get_db_client():
    client = MongoClient(host='mongodb://<dbuser>:<dbpassword>@ds237072.mlab.com:37072/gemi',
                         port=47450,
                         username='roxy',
                         password='gemicik1',
                         authSource='gemi',
                         authMechanism='SCRAM-SHA-1')

    return client


def remove_duplicates(db):
    cursor = db.yachts.aggregate(
        [
            {"$group": {"_id": "$link", "unique_ids": {"$addToSet": "$_id"}, "count": {"$sum": 1}}},
            {"$match": {"count": {"$gte": 2}}}
        ]
    )

    response = []
    for doc in cursor:
        del doc["unique_ids"][0]
        for id in doc["unique_ids"]:
            response.append(id)

    db.yachts.remove({"_id": {"$in": response}})
    print('ok')


def rename_field(db):
    db.yachts.update_many({}, {'$rename': {"added_within_x_days": "days_on_market"}})


def create_index(db):
    # db.yachts.drop_index([('link', TEXT)])
    db.yachts.create_index([('link', TEXT)], unique=True)  # prevent duplicate ads next time


if __name__ == "__main__":
    client = get_db_client()
    db = client['gemi']
    print(db.yachts.index_information())
