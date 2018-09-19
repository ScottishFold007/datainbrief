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


if __name__ == "__main__":
    pass