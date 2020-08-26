import pymongo
from motor.core import AgnosticCollection, AgnosticDatabase
from motor.motor_asyncio import AsyncIOMotorClient

from app import settings

client = AsyncIOMotorClient(settings.MONGODB_URI)

database: AgnosticDatabase = client.get_database()

db_users: AgnosticCollection = database["users"]
db_users_history: AgnosticCollection = database["users_history"]
db_offers: AgnosticCollection = database["offers"]
db_bench: AgnosticCollection = database["bench"]


async def create_indexes():
    index_name = "offers_hash_uniq"
    index_information = await db_offers.index_information()
    if index_name not in index_information:
        await db_offers.create_index(
            [("hash", pymongo.TEXT)], name=index_name, unique=True
        )
