"""Functions to read statistics from MongoDB (skeleton)."""
from config import MONGO_URI, MONGO_DB, MONGO_COLLECTION
from pymongo import MongoClient

def _get_collection():
    if not MONGO_URI:
        raise RuntimeError('MONGO_URI not configured')
    client = MongoClient(MONGO_URI)
    return client[MONGO_DB][MONGO_COLLECTION]

def get_top(n: int = 5):
    col = _get_collection()
    pipeline = [
        {'$group': {'_id': '$params', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}},
        {'$limit': n}
    ]
    return list(col.aggregate(pipeline))

def get_recent(n: int = 5):
    col = _get_collection()
    cursor = col.find().sort('timestamp', -1).limit(n)
    return list(cursor)
