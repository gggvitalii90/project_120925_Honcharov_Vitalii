import os
import sys

# Надо догрузить в начале, чтобы все модули были доступны
# (в том числе для классов в других файлах, которые импортируют config)
os.system(
    f'"{sys.executable}" -m pip install '
    'pymysql pymongo python-dotenv tabulate'
)


from mysql_connector import MySQLConnector
from log_writer import LogWriter
from log_stats import LogStats
from formatter import Formatter

def menu():
    print('\n' + '=' * 79)
    print('МЕНЮ ДЛЯ ПОИСКА ФИЛЬМОВ'.center(79))
    print('=' * 79)
    print('1 — Поиск по ключевому слову')
    print('2 — Поиск по жанру и году')
    print('3 — СТАТИСТИКА')
    print('0 — Выход')
    print('=' * 79)

def menu_stats():
    print('\n' + '=' * 79)
    print('МЕНЮ СТАТИСТИКИ'.center(79))
    print('=' * 79)
    print('1 — TOP-N популярных запросов по {keyword}')
    print('2 — TOP-N популярных запросов по {genres-years}')
    print('3 — TOP-N последних уникальных запросов')
    print('0 — Назад')
    print('=' * 79)

def main():
    connector = MySQLConnector() # Вызываем класс для работы с MySQL
    log_writer = LogWriter() # Вызываем класс для записи логов в MongoDB
    log_stats = LogStats() # Вызываем класс для получения статистики из MongoDB
    
    try:
        # Метод класса MySQLConnector для подключения к БД
        connector.connect()
        print('Подключение к БД установлено.')
    except Exception as e:
        print(f'Ошибка подключения к MySQL: {e}')
        return
    
    # Методы классов LogWriter и LogStats для подключения к MongoDB
    log_writer.connect()
    log_stats.connect()
    
    while True:
        menu() # показываем меню пользователю
        choice = input('Выберите пункт меню: ').strip()
        
        if choice == '0':
            print('Выход из программы...')
            break
        
        elif choice == '1':
            keyword = input('Введите ключевое слово: ').strip()
            if keyword:
                try:
                    # Сначала получаем общее количество (для логов)
                    total_count = connector.count_by_keyword(keyword)
                    
                    if total_count == 0:
                        print('Фильмы не найдены.')
                        continue
                    
                    print(
                        f'\nВсего найдено {total_count} фильмов '
                        f'по ключевому слову "{keyword}"'
                    )
                    print('-' * 79)
                    
                    # Логируем поиск по ключевому слову
                    log_writer.write_search_log(
                        'keyword',
                        {'keyword': keyword},
                        total_count
                    )
                    
                    # Пагинация: грузим только по 10 за раз
                    page_size = 10
                    page = 0
                    
                    while True:
                        offset = page * page_size
                        
                        # Загружаем только текущую страницу
                        page_results = connector.search_by_keyword(
                            keyword,
                            limit=page_size,
                            offset=offset
                        )
                        
                        if not page_results:
                            print('Больше страниц нет.')
                            break
                        
                        end = min(offset + page_size, total_count)
                        Formatter.pretty_print_results(
                            page_results,
                            start_index=offset + 1
                        )
                        
                        # Проверяем есть ли ещё результаты
                        if end >= total_count:
                            print('Это последняя страница.')
                            break
                        
                        show_more = input(
                            'Показать ещё? [y/N]: '
                        ).strip().lower()
                        if show_more != 'y':
                            break
                        page += 1
                        
                except Exception as e:
                    print(f'Ошибка поиска: {e}')
            else:
                print('Ключевое слово не может быть пустым.')

        
        elif choice == '2':
            try:
                # Получаем список всех жанров
                genres = connector.get_genres()
                
                # Выводим нумерованный список жанров
                print('\n' + '-' * 79)
                print('ДОСТУПНЫЕ ЖАНРЫ:'.center(79))
                print('-' * 79)
                for idx, g in enumerate(genres, start=1):
                    year_from = g['year_from'] if g['year_from'] else '?'
                    # На случай если в категории нет фильмов вообще 
                    # — тогда MIN(f.release_year) вернёт NULL из SQL
                    year_to = g['year_to'] if g['year_to'] else '?'
                    print(
                        f'{idx}: {g["name"]} '
                        f'(годы в базе: {year_from}-{year_to})'
                    )
                print('-' * 79)
                
                # Пользователь выбирает жанр по номеру
                genre_id = int(input('Введите номер жанра: ').strip())
                if 1 <= genre_id <= len(genres):
                    selected_genre = genres[genre_id - 1] 
                    # так как нумерация с 1, а индексы в списке с 0
                else:
                    print('Неверный номер жанра.')
                    continue
                
                year_from = int(input('С какого года: ').strip())
                year_to = int(input('До какого года: ').strip())
                
                # Сначала получаем общее количество (для логов)
                total_count = connector.count_by_genre_and_year(
                    selected_genre['name'], year_from, year_to
                )
                
                if total_count == 0:
                    print('Фильмы не найдены.')
                    continue
                
                print(
                    f"\nВсего фильмов для жанра '{selected_genre['name']}' "
                    f"за период {year_from}-{year_to}: {total_count}"
                )
                print('-' * 79)
                
                # Логируем поиск по жанру и году
                log_writer.write_search_log(
                    'genre_and_year',
                    {
                        'genre': selected_genre['name'],
                        'year_from': year_from,
                        'year_to': year_to
                    },
                    total_count
                )
                
                # Пагинация: грузим только по 10 за раз
                page_size = 10
                page = 0
                
                while True:
                    offset = page * page_size
                    
                    # Загружаем только текущую страницу
                    page_results = connector.search_by_genre_and_year(
                        selected_genre['name'],
                        year_from, year_to,
                        limit=page_size,
                        offset=offset
                    )
                    
                    if not page_results:
                        print('Больше страниц нет.')
                        break
                    
                    end = min(offset + page_size, total_count)
                    Formatter.pretty_print_results(
                        page_results,
                        start_index=offset + 1
                    )
                    
                    # Проверяем есть ли ещё результаты
                    if end >= total_count:
                        print('Это последняя страница.')
                        break
                    
                    show_more = input(
                        'Показать ещё? [y/N]: '
                    ).strip().lower()
                    if show_more != 'y':
                        break
                    page += 1
                    
            except ValueError:
                print('Неверный формат ввода.')
            except Exception as e:
                print(f'Ошибка поиска: {e}')
        
        elif choice == '3':
            if not log_stats.connected:
                print(
                    '\nСтатистика недоступна: '
                    'MongoDB не подключен.'
                )
                continue
            
            while True:
                menu_stats()
                stat_choice = input('Выберите пункт: ').strip()
                
                if stat_choice == '0':
                    break
                
                elif stat_choice == '1':
                    # TOP-N популярных запросов по keyword
                    try:
                        n = int(input('Сколько TOP результатов показать? ').strip())
                        if n <= 0:
                            print('Число должно быть больше 0.')
                            continue
                        top_keyword = log_stats.get_top(n, 'keyword')
                        if top_keyword:
                            print(
                                f'\n=== '
                                f'TOP-{n} популярных '
                                f'запросов {{keyword}} '
                                f'==='
                            )
                            headers = ['№', 'Ключевое слово', 'Кол-во']
                            rows = []
                            for i, item in enumerate(top_keyword, start=1):
                                keyword = item['_id'].get('keyword', '?')
                                count = item['count']
                                rows.append([i, keyword, count])
                            Formatter.pretty_print_stats(headers, rows)
                        else:
                            print(
                                'Нет данных '
                                'о поисках.'
                            )
                    except ValueError:
                        print('Введите корректное число.')
                    except Exception as e:
                        print(
                            f'Ошибка: {e}'
                        )
                
                elif stat_choice == '2':
                    # TOP-N популярных запросов по genres-years
                    try:
                        n = int(input('Сколько TOP результатов показать? ').strip())
                        if n <= 0:
                            print('Число должно быть больше 0.')
                            continue
                        top_genre = log_stats.get_top(n, 'genre_and_year')
                        if top_genre:
                            print(
                                f'\n=== '
                                f'TOP-{n} популярных '
                                f'запросов '
                                f'{{genres-years}} ==='
                            )
                            headers = ['№', 'Жанр', 'Период', 'Кол-во']
                            rows = []
                            for i, item in enumerate(top_genre, start=1):
                                genre = item['_id'].get('genre', '?')
                                year_from = item['_id'].get('year_from', '?')
                                year_to = item['_id'].get('year_to', '?')
                                count = item['count']
                                rows.append(
                                    [i, genre, f'{year_from}-{year_to}', count]
                                )
                            Formatter.pretty_print_stats(headers, rows)
                        else:
                            print(
                                'Нет данных '
                                'о поисках.'
                            )
                    except ValueError:
                        print('Введите корректное число.')
                    except Exception as e:
                        print(
                            f'Ошибка: {e}'
                        )
                
                elif stat_choice == '3':
                    # TOP-N последних запросов
                    try:
                        n = int(input('Сколько последних запросов показать? ').strip())
                        if n <= 0:
                            print('Число должно быть больше 0.')
                            continue
                        recent = log_stats.get_recent(n)
                        if recent:
                            print(
                                f'\n=== '
                                f'TOP-{n} последних '
                                f'уникальных запросов ==='
                            )
                            headers = ['№', 'Дата', 'Тип поиска', 'Параметры', 'Количество']
                            rows = []
                            for i, item in enumerate(recent, start=1):
                                timestamp = item.get('timestamp', '')
                                search_type = item['search_type']
                                params = item['params']
                                count = item['count']
                                rows.append(
                                    [i, timestamp, search_type, str(params), count]
                                )
                            Formatter.pretty_print_stats(headers, rows)
                        else:
                            print(
                                'Нет данных '
                                'о поисках.'
                            )
                    except ValueError:
                        print('Введите корректное число.')
                    except Exception as e:
                        print(
                            f'Ошибка: {e}'
                        )
                
                else:
                    print(
                        'Неизвестная '
                        'опция, '
                        'попробуйте снова.'
                    )
        
        else:
            print('Неизвестная опция, попробуйте снова.')
    
    connector.close()
    log_writer.close()
    log_stats.close()
    print('Отключение от БД и MongoDB.')

if __name__ == '__main__':
    main()
