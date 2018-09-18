from pymongo import MongoClient, IndexModel, ASCENDING, DESCENDING, TEXT, HASHED


def get_db_client():
    client = MongoClient(host='mongodb://<dbuser>:<dbpassword>@ds237072.mlab.com:37072/gemi',
                         port=47450,
                         username='roxy',
                         password='gemicik1',
                         authSource='gemi',
                         authMechanism='SCRAM-SHA-1')

    return client


def get_db():
    client = get_db_client()
    database = client['gemi']
    return database


db = get_db()


def remove_duplicates():
    print('removing dups..')

    pipeline = [
        {"$group": {"_id": "$link", "unique_ids": {"$addToSet": "$_id"}, "count": {"$sum": 1}}},
        {"$match": {"count": {"$gte": 2}}}
    ]
    cursor = db.yachts.aggregate(pipeline)

    response = []
    for doc in cursor:
        del doc["unique_ids"][0]
        for unique_id in doc["unique_ids"]:
            response.append(unique_id)

    db.yachts.remove({"_id": {"$in": response}})

    print('removed dups.')


def rename_field(oldname, newname):
    db.yachts.update_many({}, {'$rename': {oldname: newname}})
    print('renamed %s to %s' % (oldname, newname))


def create_index(index_name, is_unique):
    db.yachts.create_index([(index_name, ASCENDING)], unique=is_unique)  # prevent duplicate ads next time
    print('created %s' % index_name)


def drop_index(index_name):
    db.yachts.drop_index([(index_name, TEXT)])
    print('dropped %s' % index_name)


def get_index_info():
    print(db.yachts.index_information())


def remove_doc_based_on_existence_of_a_field(field_name):
    db.yachts.delete_many({field_name: {"$exists": False}})


def remove_field(field_name):
    db.yachts.update(
        {},
        {
            '$unset': {field_name: ""}
        },
        multi=True
    )


if __name__ == "__main__":
    create_index('link', is_unique=True)
    get_index_info()