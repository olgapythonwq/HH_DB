import logging
import os
from typing import List

from config import DATA_DIR

logger = logging.getLogger(__name__)  # Создание логгера для текущего модуля


def load_employer_ids(filename: str = "employers.txt") -> List[int]:
    """Формирует список id работодателей из txt-файла"""
    filepath = os.path.join(DATA_DIR, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            employers_list = [
                int(line.strip())
                for line in file
                if line.strip() and not line.startswith("#")  # Можно добавить названия работодателей
            ]
        logger.info(f"Загружено {len(employers_list)} employer_id из {filename}")
        return employers_list
    except FileNotFoundError:
        logger.error(f"Файл {filepath} не найден.")
        return []
    except ValueError as e:
        logger.exception(f"Ошибка в формате ID в {filepath}: {e}")
        return []
