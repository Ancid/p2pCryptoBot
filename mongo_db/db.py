import os

import asyncio
# import pymongo
import motor
import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
import pymongo

client = motor.motor_asyncio.AsyncIOMotorClient(os.environ['MONGODB_URI'])

database: AsyncIOMotorDatabase = client.get_database()

# client = pymongo.MongoClient(os.environ['MONGODB_URI'])
# db = client.heroku_7xn6mnj8
db_users: AsyncIOMotorCollection = database["users"]
db_users_history: AsyncIOMotorCollection = database["users_history"]
db_offers: AsyncIOMotorCollection = database["offers"]
db_bench: AsyncIOMotorCollection = database["bench"]


async def create_indexes():
    index_name = 'offers_hash_uniq'
    index_information = await db_offers.index_information()
    if index_name not in index_information:
        await db_offers.create_index([('hash', pymongo.TEXT)], name=index_name, unique=True)
