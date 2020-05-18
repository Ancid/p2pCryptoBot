import os

import pymongo

from config import DB_MONGO_DSN

# client = pymongo.MongoClient(DB_MONGO_DSN)
client = pymongo.MongoClient(os.environ['MONGODB_URI'])
db_users = client.get_database()["users"]
db_offers = client.get_database()["offers"]

index_name = 'offers_hash_uniq'
if index_name not in db_offers.index_information():
    db_offers.create_index([('hash', pymongo.TEXT)], name=index_name, unique=True)
