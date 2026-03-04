"""MongoDB logging helper (skeleton)."""
from typing import Dict
from config import MONGO_URI, MONGO_DB, MONGO_COLLECTION
from pymongo import MongoClient
from datetime import datetime

class LogWriter:
    def __init__(self):
        self.client = None
        self.col = None

    def connect(self):
        if not MONGO_URI:
            raise RuntimeError('MONGO_URI not configured')
        self.client = MongoClient(MONGO_URI)
        self.col = self.client[MONGO_DB][MONGO_COLLECTION]

    def write_search_log(self, search_type: str, params: Dict, results_count: int):
        doc = {
            'timestamp': datetime.utcnow(),
            'search_type': search_type,
            'params': params,
            'results_count': results_count
        }
        if self.col is None:
            self.connect()
        self.col.insert_one(doc)

    def close(self):
        if self.client:
            self.client.close()
