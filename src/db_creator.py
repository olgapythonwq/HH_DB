import logging
from typing import Any

import psycopg2

logger = logging.getLogger(__name__)  # Создание логгера для текущего модуля


def create_database(database_name: str, params: dict) -> None:
    """Создание БД и таблиц для сохранения данных о каналах и видео."""
    conn = psycopg2.connect(dbname='postgres', **params)  # создаём объект коннекшн
    conn.autocommit = True  # чтобы автокомитился каждый SQL-запрос, иначе ошибка
    cur = conn.cursor()  # создаём объект курсор из объекта коннекшн
    # пишем SQL-команды
    try:
        logger.info(f"Удаляем БД {database_name}, если существует...")
        # лучше сначала дропнуть БД, чтобы при повторном запуске не было проблем
        cur.execute(f"DROP DATABASE IF EXISTS {database_name}")
    except Exception as e:
        print(f'Информация: {e}')
    # else:
    # Исключений не произошло, БД дропнута
    finally:
        logger.info(f"Создаём новую БД: {database_name}")
        cur.execute(f"CREATE DATABASE {database_name}")
    cur.close()
    conn.close()
    logger.info(f"База данных {database_name} успешно создана.")


def create_tables_in_db(database_name: str, params: dict) -> None:
    # подключимся к созданной БД
    conn = psycopg2.connect(dbname=database_name, **params)
    # создадим таблицу employers
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS employers (
                employer_id BIGINT PRIMARY KEY,
                employer_name VARCHAR(255) NOT NULL,
                employer_rating REAL,
                employer_reviews INTEGER
            )
        """)
    # создадим таблицу vacancies
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS vacancies (
                vacancy_id SERIAL PRIMARY KEY,
                vacancy_name VARCHAR(255) NOT NULL,
                employer_id BIGINT REFERENCES employers(employer_id),
                salary_from INTEGER,
                salary_to INTEGER,
                publish_date DATE,
                vacancy_url TEXT
            )
        """)
    conn.commit()
    conn.close()


def save_data_to_database(data: list[dict[str, Any]], database_name: str, params: dict) -> None:
    """Сохранение данных о работодателях и вакансиях в БД."""
    conn = psycopg2.connect(dbname=database_name, **params)  # подключаемся к БД
    with conn.cursor() as cur:
        # 1. Сохраняем работодателей (уникальных)
        saved_employers = set()
        for item in data:
            employer = item.get("employer")
            if employer is None:
                continue
            employer_id = int(employer.get("id"))
            if employer_id in saved_employers:
                continue  # не вставляем повторно

            employer_stats = employer.get("employer_rating", {})
            cur.execute("""
                INSERT INTO employers (employer_id, employer_name, employer_rating, employer_reviews)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (employer_id) DO NOTHING
                """,
                        (employer_id, employer.get("name"), employer_stats.get("total_rating"),
                         employer_stats.get("reviews_count"),
                         )
                        )
            saved_employers.add(employer_id)
        # 2. Сохраняем вакансии
        for item in data:
            employer = item.get("employer")
            if employer is None:
                continue
            employer_id = int(employer.get("id"))
            salary = item.get("salary") or {}
            salary_from = salary.get("from")
            salary_to = salary.get("to")
            cur.execute("""
                INSERT INTO vacancies (vacancy_name, employer_id, salary_from, salary_to, publish_date, vacancy_url)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                        (item.get("name"), employer_id, salary_from, salary_to, item.get("published_at"),
                         item.get("alternate_url")
                         )
                        )
    conn.commit()
    conn.close()
