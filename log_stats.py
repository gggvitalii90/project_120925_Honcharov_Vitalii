"""MongoDB statistics helper."""
from config import MONGO_URI, MONGO_DB, MONGO_COLLECTION
from pymongo import MongoClient

class LogStats:
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

    def get_top(self, n: int = 5, search_type: str = None):
        if search_type is None:
            print('Ошибка: search_type не передан')
            return []
        
        # Для разных типов поиска разные структуры params,
        # поэтому используем разные pipelines с $toLower 
        # для case-insensitive группировки
        if search_type == 'keyword':
            pipeline = [
                {'$match': {'search_type': search_type}},
                {
                    '$group': {
                        '_id': {
                            'keyword': {'$toLower': '$params.keyword'}
                        },
                        'count': {'$sum': 1}
                    }
                },
                {'$sort': {'count': -1}},
                {'$limit': n}
            ]
        elif search_type == 'genre_and_year':
            pipeline = [
                {'$match': {'search_type': search_type}},
                {
                    '$group': {
                        '_id': {
                            'genre': {'$toLower': '$params.genre'},
                            'year_from': '$params.year_from',
                            'year_to': '$params.year_to'
                        },
                        'count': {'$sum': 1}
                    }
                },
                {'$sort': {'count': -1}},
                {'$limit': n}
            ]
        else:
            return []
        
        result = list(self.col.aggregate(pipeline))
        return result

    def get_recent(self, n: int = 5):
        """Получить последние N УНИКАЛЬНЫХ поисков."""
        pipeline = [
            # Шаг 1: Группируем по ключу (search_type + params)
            {
                '$group': {
                    '_id': {
                        'search_type': '$search_type',
                        'params': '$params'
                    },
                    'timestamp': {'$max': '$timestamp'},  # Последняя дата
                    'search_type': {'$first': '$search_type'},
                    'params': {'$first': '$params'},
                    'count': {'$sum': 1}  # Сколько раз делали этот запрос
                }
            },
            
            # Шаг 2: Сортируем по дате (новые первые)
            {'$sort': {'timestamp': -1}},
            
            # Шаг 3: Берём первые N
            {'$limit': n}
        ]
        
        result = list(self.col.aggregate(pipeline))
        return result

    def close(self):
        if self.client:
            self.client.close()
