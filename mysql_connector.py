"""Stub for MySQL connector and search functions."""
from typing import List, Dict
from config import MYSQL_CONFIG
import pymysql

class MySQLConnector:
    def __init__(self):
        self.conn = None

    def connect(self):
        cfg = MYSQL_CONFIG
        self.conn = pymysql.connect(host=cfg['host'], port=cfg['port'], user=cfg['user'],
                                    password=cfg['password'], db=cfg['db'], charset='utf8mb4')
        return self.conn

    def close(self):
        if self.conn:
            self.conn.close()

    def get_genres(self) -> List[str]:
        # Return list of genres from DB
        with self.conn.cursor() as cur:
            cur.execute('SELECT name FROM genre')
            rows = cur.fetchall()
        return [r[0] for r in rows]

    def search_by_keyword(self, keyword: str, limit: int = 10) -> List[Dict]:
        q = "SELECT film_id, title, description, release_year FROM film WHERE title LIKE %s LIMIT %s"
        with self.conn.cursor() as cur:
            cur.execute(q, (f"%{keyword}%", limit))
            rows = cur.fetchall()
        return [{'film_id': r[0], 'title': r[1], 'description': r[2], 'year': r[3]} for r in rows]

    def search_by_genre_and_year(self, genre: str, year_from: int, year_to: int, limit: int = 10):
        # Implement appropriate join with film_category/film tables
        raise NotImplementedError('search_by_genre_and_year not implemented yet')
