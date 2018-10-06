from pymongo import MongoClient


def get_client():
    return MongoClient(host='mongodb://<dbuser>:<dbpassword>@ds237072.mlab.com:37072/gemi',
                       port=47450,
                       username='roxy',
                       password='gemicik1',
                       authSource='gemi',
                       authMechanism='SCRAM-SHA-1')


def get_client_and_db():
    client = get_client()
    database = client['gemi']
    return client, database


if __name__ == "__main__":
    pass
