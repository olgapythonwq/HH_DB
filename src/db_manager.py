import json
import os

import psycopg2

from config import DATA_DIR


class DBManager:

    def __init__(self, dbname: str, db_config: dict[str, str]):
        self.conn = psycopg2.connect(dbname=dbname, **db_config)  # подключение к уже существующей БД
        self.cur = self.conn.cursor()

    def get_companies_and_vacancies_count(self):
        """Метод, получающий список всех компаний и количество вакансий у каждой компании и записывающий в """
        filepath = os.path.join(DATA_DIR, "vacancies_per_employer.json")
        with self.conn:
            self.cur.execute("""
            SELECT employer_id,
                   employer_name,
                   employer_rating,
                   employer_reviews,
                   COUNT(vacancy_name) AS nb_of_vacancies
            FROM vacancies
            JOIN employers USING(employer_id)
            GROUP BY vacancies.employer_id, employers.employer_name, employers.employer_rating,
            employers.employer_reviews
            ORDER BY nb_of_vacancies DESC
            """)
            data = self.cur.fetchall()
            data_dict = [
                {"employer_id": d[0],
                 "employer_name": d[1],
                 "employer_rating": d[2],
                 "employer_reviews": d[3],
                 "nb_of_vacancies": d[4]
                 } for d in data]
            with open(filepath, "w", encoding='utf-8') as f:
                json.dump(data_dict, f, indent=4, ensure_ascii=False)

    def get_all_vacancies(self):
        """Метод, получающий список всех вакансий с указанием названия компании, названия вакансии,
        зарплаты и ссылки на вакансию"""
        with self.conn:
            self.cur.execute("""
            SELECT vacancy_id,
                   vacancy_name,
                   employer_id,
                   employer_name,
                   salary_from,
                   salary_to,
                   vacancy_url
            FROM vacancies
            JOIN employers USING(employer_id)
            ORDER BY vacancies.vacancy_id
            """)
            data = self.cur.fetchall()
            result = [
                {"vacancy_id": d[0],
                 "vacancy_name": d[1],
                 "employer_id": d[2],
                 "employer_name": d[3],
                 "salary_from": d[4],
                 "salary_to": d[5],
                 "vacancy_url": d[6]
                 } for d in data]
            return result

    def get_avg_salary(self):
        """Метод, получающий среднюю зарплату по вакансиям. Метод использует:
            - среднее из salary_from и salary_to, если указаны оба
            - только salary_from, если указано только оно
            - только salary_to, если указано только оно"""
        with self.conn:
            self.cur.execute("""
                SELECT AVG(
                    CASE
                        WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL THEN (salary_from + salary_to) / 2.0
                        WHEN salary_from IS NOT NULL THEN salary_from
                        WHEN salary_to IS NOT NULL THEN salary_to
                        ELSE NULL
                    END
                )
                FROM vacancies
                WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
            """)
            result = self.cur.fetchone()[0]
            return round(result, 2) if result else 0.0

    def get_vacancies_with_higher_salary(self):
        """Метод, получающий список всех вакансий, у которых зарплата выше средней по всем вакансиям"""
        with self.conn:
            self.cur.execute("""
             WITH avg_salary AS (
                SELECT AVG(
                    CASE
                        WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL THEN (salary_from + salary_to) / 2.0
                        WHEN salary_from IS NOT NULL THEN salary_from
                        WHEN salary_to IS NOT NULL THEN salary_to
                        ELSE NULL
                    END
                ) AS value
                FROM vacancies
                WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
            )
            SELECT vacancy_id,
                   vacancy_name,
                   employer_id,
                   employer_name,
                   salary_from,
                   salary_to,
                   vacancy_url
            FROM vacancies
            JOIN employers USING(employer_id), avg_salary
            WHERE CASE
                    WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL THEN (salary_from + salary_to) / 2.0
                    WHEN salary_from IS NOT NULL THEN salary_from
                    WHEN salary_to IS NOT NULL THEN salary_to
                    ELSE NULL
                END > avg_salary.value
            ORDER BY vacancies.salary_from NULLS LAST
            """)
            data = self.cur.fetchall()
            result = [
                {"vacancy_id": d[0],
                 "vacancy_name": d[1],
                 "employer_id": d[2],
                 "employer_name": d[3],
                 "salary_from": d[4],
                 "salary_to": d[5],
                 "vacancy_url": d[6]
                 } for d in data]
            return result

    def get_vacancies_with_keyword(self, user_input):
        """Метод, получающий список всех вакансий, в названии которых содержатся переданные в метод слова"""
        with self.conn:
            # ILIKE вместо LIKE, чтобы не приводить к нижнему регистру
            # подставляем через плейсхолдер %s, а не f-строку
            self.cur.execute("""
                   SELECT vacancy_id,
                          vacancy_name,
                          employer_id,
                          employer_name,
                          salary_from,
                          salary_to,
                          vacancy_url
                   FROM vacancies
                   JOIN employers USING(employer_id)
                   WHERE vacancy_name ILIKE %s
                   ORDER BY vacancies.vacancy_id
                   """, (f"%{user_input}%",))
            data = self.cur.fetchall()
            result = [
                {"vacancy_id": d[0],
                 "vacancy_name": d[1],
                 "employer_id": d[2],
                 "employer_name": d[3],
                 "salary_from": d[4],
                 "salary_to": d[5],
                 "vacancy_url": d[6]
                 } for d in data]
            return result
