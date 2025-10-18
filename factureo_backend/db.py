from pymongo import MongoClient
from bson.objectid import ObjectId
from config import config

client = MongoClient(config.MONGO_URI)
db = client.get_default_database()
if db is None:
    db = client.get_database("factureo")


def collection(name: str):
    return db[name]


__all__ = ["db", "collection", "ObjectId"]
