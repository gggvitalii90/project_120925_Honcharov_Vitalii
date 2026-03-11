"""MongoDB logging helper (skeleton)."""
from typing import Dict
from config import MONGO_URI, MONGO_DB, MONGO_COLLECTION
from pymongo import MongoClient
from datetime import datetime

class LogWriter:
    def __init__(self):
        self.client = None
        self.col = None
        self.connected = False

    def connect(self):
        try:
            self.client = MongoClient(MONGO_URI)
            self.col = self.client[MONGO_DB][MONGO_COLLECTION]
            self.connected = True
        except Exception as e:
            print(f'Ошибка подключения к MongoDB: {e}')
            self.connected = False

    def write_search_log(
            self, search_type: str, params: Dict, results_count: int
            ):
        if not self.connected:
            return  # Если MongoDB не подключен, ничего не делаем
        
        doc = {
            'timestamp': datetime.utcnow(),
            'search_type': search_type,
            'params': params,
            'results_count': results_count
        }
        self.col.insert_one(doc)

    def close(self):
        if self.client:
            self.client.close()
