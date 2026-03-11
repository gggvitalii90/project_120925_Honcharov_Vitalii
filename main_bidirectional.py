from math import ceil
from mysql_connector import MySQLConnector


def menu():
    print('\n=== Поиск Фильмов ===')
    print('1 — Поиск по ключевому слову')
    print('2 — Поиск по жанру и году')
    print('3 — Топ поисков')
    print('4 — Недавние поиски')
    print('0 — Выход')


def display_results(results):
    if not results:
        print('Результатов не найдено.')
        return

    print('-' * 80)
    header = (
        f"| {'№':^3} | {'Название':^30} | "
        f"{'Жанр':^15} | {'Год':^6} | {'ID':^6} |"
    )
    print(header)
    print('-' * 80)

    for i, item in enumerate(results, start=1):
        title = item['title'][:30]
        genre = item.get('genre', '')
        year = item['year']
        film_id = item['film_id']
        row = (
            f"| {i:^3} | {title:<30} | "
            f"{genre:<15} | {year:^6} | {film_id:^6} |"
        )
        print(row)

    print('-' * 80)


def search_with_bidirectional_paging(connector, genre_name, year_from, year_to):
    total_count = connector.count_by_genre_and_year(
        genre_name, year_from, year_to
    )

    if total_count == 0:
        print('Фильмы не найдены.')
        return

    print(
        f"\nВсего фильмов для жанра '{genre_name}' "
        f"за период {year_from}-{year_to}: {total_count}"
    )
    print('-' * 79)

    page_size = 10
    total_pages = ceil(total_count / page_size)
    page = 0

    while True:
        offset = page * page_size
        page_results = connector.search_by_genre_and_year(
            genre_name,
            year_from,
            year_to,
            limit=page_size,
            offset=offset
        )

        if not page_results:
            print('Нет данных для отображения.')
            return

        start = offset + 1
        end = min(offset + page_size, total_count)
        print(
            f"Страница {page + 1}/{total_pages} "
            f"({start}-{end} из {total_count})"
        )
        display_results(page_results)

        if total_pages == 1:
            break

        command = input(
            'Команды: [n] дальше, [p] назад, [q] выход: '
        ).strip().lower()

        if command == 'n':
            if page + 1 < total_pages:
                page += 1
            else:
                print('Это последняя страница.')
        elif command == 'p':
            if page > 0:
                page -= 1
            else:
                print('Это первая страница.')
        else:
            break


def main():
    connector = MySQLConnector()

    try:
        connector.connect()
        print('Подключение к БД установлено.')
    except Exception as exc:
        print(f'Ошибка подключения: {exc}')
        return

    while True:
        menu()
        choice = input('Выберите пункт меню: ').strip()

        if choice == '0':
            print('Выход из программы...')
            break

        elif choice == '1':
            keyword = input('Введите ключевое слово: ').strip()
            if keyword:
                try:
                    results = connector.search_by_keyword(keyword)
                    print(f'\nНайдено {len(results)} фильмов:')
                    display_results(results)
                except Exception as exc:
                    print(f'Ошибка поиска: {exc}')
            else:
                print('Ключевое слово не может быть пустым.')

        elif choice == '2':
            try:
                genres = connector.get_genres()

                print('\n' + '-' * 79)
                print('Доступные жанры:'.center(79))
                print('-' * 79)
                for idx, genre_data in enumerate(genres, start=1):
                    db_year_from = genre_data['year_from']
                    db_year_to = genre_data['year_to']
                    print(
                        f"{idx}: {genre_data['name']} "
                        f"(годы в базе: {db_year_from}-{db_year_to})"
                    )
                print('-' * 79)

                genre_id = int(input('Введите номер жанра: ').strip())
                if not (1 <= genre_id <= len(genres)):
                    print('Неверный номер жанра.')
                    continue

                selected_genre = genres[genre_id - 1]['name']
                year_from = int(input('С какого года: ').strip())
                year_to = int(input('До какого года: ').strip())

                search_with_bidirectional_paging(
                    connector,
                    selected_genre,
                    year_from,
                    year_to
                )

            except ValueError:
                print('Неверный формат ввода.')
            except Exception as exc:
                print(f'Ошибка поиска: {exc}')

        elif choice == '3':
            print('Топ поисков — не реализовано')

        elif choice == '4':
            print('Недавние поиски — не реализовано')

        else:
            print('Неизвестная опция, попробуйте снова.')

    connector.close()
    print('Отключение от БД.')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nПрограмма прервана')
