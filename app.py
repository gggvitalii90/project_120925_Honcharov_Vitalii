"""Flask веб-интерфейс для поиска фильмов."""
import os
from flask import Flask, render_template, request

from mysql_connector import MySQLConnector
from mongo_connector import MongoConnector
from log_writer import LogWriter
from log_stats import LogStats

app = Flask(__name__)

PAGE_SIZE = 10


def get_connections():
    """Создаёт подключения к MySQL и MongoDB."""
    mysql_conn = MySQLConnector()
    mysql_conn.connect()

    mongo_conn = MongoConnector()
    mongo_conn.connect()

    log_writer = LogWriter(mongo_conn)
    log_stats = LogStats(mongo_conn)

    return mysql_conn, mongo_conn, log_writer, log_stats


@app.route('/')
def index():
    """Главная страница с формой поиска."""
    # Загружаем жанры для выпадающего списка
    mysql_conn = MySQLConnector()
    try:
        mysql_conn.connect()
        genres = mysql_conn.get_genres()
    except Exception:
        genres = []
    finally:
        mysql_conn.close()

    return render_template('index.html', genres=genres)


@app.route('/search')
def search():
    """Обработка поиска и вывод результатов."""
    search_type = request.args.get('search_type', 'keyword')
    page = int(request.args.get('page', 1))
    offset = (page - 1) * PAGE_SIZE

    mysql_conn, mongo_conn, log_writer, log_stats = get_connections()

    try:
        genres = mysql_conn.get_genres()
        results = []
        total_count = 0
        error = None

        if search_type == 'keyword':
            keyword = request.args.get('keyword', '').strip()
            if not keyword:
                return render_template(
                    'index.html', genres=genres,
                    error='Введите ключевое слово.'
                )

            total_count = mysql_conn.count_by_keyword(keyword)
            results = mysql_conn.search_by_keyword(
                keyword, limit=PAGE_SIZE, offset=offset
            )

            # Логируем только первую страницу
            if page == 1:
                try:
                    log_writer.write_search_log(
                        'keyword', {'keyword': keyword}, total_count
                    )
                except Exception:
                    pass

        elif search_type == 'genre_and_year':
            genre = request.args.get('genre', '').strip()
            year_from = request.args.get('year_from', '').strip()
            year_to = request.args.get('year_to', '').strip()

            if not genre or not year_from or not year_to:
                return render_template(
                    'index.html', genres=genres,
                    error='Заполните все поля: жанр, год от, год до.'
                )

            try:
                year_from_int = int(year_from)
                year_to_int = int(year_to)
            except ValueError:
                return render_template(
                    'index.html', genres=genres,
                    error='Годы должны быть числами.'
                )

            total_count = mysql_conn.count_by_genre_and_year(
                genre, year_from_int, year_to_int
            )
            results = mysql_conn.search_by_genre_and_year(
                genre, year_from_int, year_to_int,
                limit=PAGE_SIZE, offset=offset
            )

            if page == 1:
                try:
                    log_writer.write_search_log(
                        'genre_and_year',
                        {'genre': genre,
                         'year_from': year_from_int,
                         'year_to': year_to_int},
                        total_count
                    )
                except Exception:
                    pass

        total_pages = (total_count + PAGE_SIZE - 1) // PAGE_SIZE

        return render_template(
            'index.html',
            genres=genres,
            results=results,
            total_count=total_count,
            page=page,
            total_pages=total_pages,
            search_type=search_type,
            keyword=request.args.get('keyword', ''),
            genre=request.args.get('genre', ''),
            year_from=request.args.get('year_from', ''),
            year_to=request.args.get('year_to', ''),
        )

    except Exception as e:
        return render_template(
            'index.html', genres=[], error=f'Ошибка: {e}'
        )
    finally:
        mysql_conn.close()
        mongo_conn.close()


@app.route('/stats')
def stats():
    """Страница статистики поисков."""
    mongo_conn = MongoConnector()
    mongo_conn.connect()
    log_stats = LogStats(mongo_conn)

    from flask import request
    top_n = request.args.get('top_n', default=5, type=int)
    tab = request.args.get('tab', default='keyword')
    top_keyword = []
    top_genre = []
    recent = []

    if log_stats.is_connected():
        try:
            top_keyword = log_stats.get_top(n=top_n, search_type='keyword')
            top_genre = log_stats.get_top(n=top_n, search_type='genre_and_year')
            recent = log_stats.get_recent(n=top_n)
        except Exception:
            pass

    mongo_conn.close()

    return render_template(
        'stats.html',
        top_keyword=top_keyword,
        top_genre=top_genre,
        recent=recent,
        connected=mongo_conn.connected or bool(top_keyword or top_genre or recent),
        top_n=top_n,
        active_tab=tab
    )


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
