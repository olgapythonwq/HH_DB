import json
import logging

from src.db_manager import DBManager

logger = logging.getLogger(__name__)  # Создание логгера для текущего модуля


def run_application(db: DBManager) -> None:
    """Запускает приложение для взаимодействия с пользователем."""
    print('Приветствую в приложении по поиску и анализу вакансий на HH.ru.\n')
    while True:
        print("\nДоступный функционал приложения")
        print("1. Вывести доступных работодателей и количество вакансий у каждой компании")
        print("2. Получить список всех вакансий с указанием названия компании, названия вакансии, зарплаты и ссылок")
        print("3. Получить среднюю зарплату по вакансиям")
        print("4. Получить вакансии, у которых зарплата выше средней по всем вакансиям")
        print("5. Получить вакансии, в названии которых содержатся переданные слова")
        print("6. Выйти")

        choice = input("Выберите номер действия: ")
        logger.info(f"Пользователь выбрал действие: {choice}")

        if choice == "1":
            with open("data/vacancies_per_employer.json", "r", encoding="utf-8") as f:
                summary = json.load(f)
            logger.info(f"Отобрано {len(summary)} работодателей")
            for item in summary:
                print(f"{item['employer_name']} — {item['nb_of_vacancies']} вакансий")

        elif choice == "2":
            all_vacancies = db.get_all_vacancies()
            logger.info(f"Найдено {len(all_vacancies)} вакансий")
            for vac in all_vacancies:
                print(vac)

        elif choice == "3":
            avg_salary = db.get_avg_salary()
            logger.info(f"Средняя зарплата по вакансиям: {avg_salary}")
            print(avg_salary)

        elif choice == "4":
            vacancies_with_higher_salary = db.get_vacancies_with_higher_salary()
            logger.info(f"{len(vacancies_with_higher_salary)} вакансий, у которых зарплата выше выбраны")
            print(vacancies_with_higher_salary)

        elif choice == "5":
            user_input = input('Введите ключевое слово (или фразу) для поиска в названии: ')
            logger.info(f"Пользователь ввёл ключевую фразу для фильтрации: '{user_input}'")

            filtered_vacancies = db.get_vacancies_with_keyword(user_input)
            logger.info(f"Найдено {len(filtered_vacancies)} вакансий по ключевой фразе '{user_input}'")
            for vac in filtered_vacancies:
                print(vac)

        elif choice == "6":
            print("Выход.")
            break
        else:
            logger.warning(f"Неверный выбор пользователя: {choice}")
            print("Неверный выбор.")
