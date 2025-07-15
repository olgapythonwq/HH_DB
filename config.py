import os

from dotenv import load_dotenv

# Абсолютный путь к корневой папке проекта
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Пути к логам и данным
LOGS_DIR = os.path.join(BASE_DIR, "logs")
DATA_DIR = os.path.join(BASE_DIR, "data")

# Конкретные файлы
LOG_FILE_PATH = os.path.join(LOGS_DIR, "app.log")


# Загружаем переменные окружения из .env файла
load_dotenv()
# Формируем словарь с параметрами подключения к БД из переменных окружения
DB_CONFIG = {
    "user": os.getenv("user"),
    "password": os.getenv("password"),
    "host": os.getenv("host", "localhost"),
    "port": os.getenv("port", "5432"),
}

DB_NAME = os.getenv("postgres", "vac_db")
