"""Stub for MySQL connector and search functions."""
from config import MYSQL_CONFIG # подключаем наш файл конфигурации, который содержит настройки для подключения к MySQL и MongoDB
import pymysql

class MySQLConnector: # попробуем структурировать все через класс, не факт что это нужно для такого простого случая, но так будет удобнее расширять функциональность в будущем
    def __init__(self):
        self.conn = None

    def connect(self): # подключаемся к MySQL используя настройки из конфигурации
        config = MYSQL_CONFIG
        self.conn = pymysql.connect(host=config['host'], port=config['port'], user=config['user'],
                                    password=config['password'], db=config['db'], charset='utf8mb4')
        return self.conn

    def close(self): # закрываем соединение с MySQL, если оно было открыто
        if self.conn:
            self.conn.close()

    def get_genres(self):
        # Получаем список жанров фильмов
        with self.conn.cursor() as cur:
            cur.execute('SELECT name FROM category')
            rows = cur.fetchall() # fetchall возвращает список кортежей, например: [('Action',), ('Comedy',), ...]
        return [r[0] for r in rows]

    def search_by_keyword(self, keyword: str, limit: int = 10):
        # Возвращает список словарей фильмов: [{'film_id': 1, 'title': 'Alien', ...}, ...]
        q = "SELECT film_id, title, description, release_year FROM film WHERE title LIKE %s LIMIT %s"
        with self.conn.cursor() as cur:
            cur.execute(q, (f"%{keyword}%", limit))
            rows = cur.fetchall()
        return [{'film_id': r[0], 'title': r[1], 'description': r[2], 'year': r[3]} for r in rows]

    def search_by_genre_and_year(self, category_name: str, year_from: int, year_to: int, limit: int = 10):
        # Ищем фильмы по категории (жанру) и диапазону годов
        q = """
            SELECT f.film_id, f.title, f.description, f.release_year
            FROM film AS f
            JOIN film_category AS fc ON fc.film_id = f.film_id
            JOIN category AS c ON c.category_id = fc.category_id
            WHERE c.name = %s
              AND f.release_year BETWEEN %s AND %s
            ORDER BY f.title
            LIMIT %s
        """
        with self.conn.cursor() as cur:
            cur.execute(q, (category_name, year_from, year_to, limit))
            rows = cur.fetchall()
        return [{'film_id': r[0], 'title': r[1], 'description': r[2], 'year': r[3]} for r in rows]
