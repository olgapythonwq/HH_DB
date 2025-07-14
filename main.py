import logging
import os

from config import DB_CONFIG, DB_NAME, LOG_FILE_PATH
from src.api import HeadHunterAPI
from src.db_creator import create_database, create_tables_in_db, save_data_to_database
from src.db_manager import DBManager
from src.interface import run_application
from src.utils import load_employer_ids

# Создание директорий для логов, если они отсутствуют
os.makedirs("logs", exist_ok=True)


# Настройка логирования: в файл и консоль
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                    handlers=[logging.FileHandler(LOG_FILE_PATH, encoding="utf-8"),
                              logging.StreamHandler()])


def main() -> None:
    """Точка входа в приложение. Инициализирует API-клиент, создаёт БД для хранения данных в таблицах и запускает
    пользовательский интерфейс для взаимодействия с вакансиями."""
    logging.info("Запуск приложения")
    ids = load_employer_ids()  # Получение списка работодателей
    # print(ids)
    api = HeadHunterAPI()  # Создаём экземпляр класса
    vacancies = api.get_vacancies_of_employers(ids)
    # print(vacancies)

    create_database(DB_NAME, DB_CONFIG)
    create_tables_in_db(DB_NAME, DB_CONFIG)
    save_data_to_database(vacancies, DB_NAME, DB_CONFIG)
    db = DBManager(DB_NAME, DB_CONFIG)
    db.get_companies_and_vacancies_count()
    run_application(db)


if __name__ == "__main__":
    main()
