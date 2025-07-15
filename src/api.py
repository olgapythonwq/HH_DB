import logging
import time
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)  # Создание логгера для текущего модуля


class HeadHunterAPI():
    """Класс для получения данных с сайта hh.ru"""

    def __init__(self) -> None:
        """Инициализирует базовый URL для запросов к API hh.ru."""
        self.base_url: str = "https://api.hh.ru/vacancies"
        logger.info("HeadHunterAPI инициализирован.")

    def get_vacancies_of_employers(self, employers_list: list[int]) -> List[Dict[str, Any]]:
        """Метод, формирующий запрос и возвращающий список вакансий от указанных работодателей."""
        all_vacancies = []
        for employer_id in employers_list:
            logger.info(f"Загружаем вакансии для работодателя {employer_id}")
            page = 0
            while True:
                params = {
                    "employer_id": employer_id,
                    "page": page,
                    "per_page": 100
                }
                try:
                    response = requests.get(self.base_url, params=params, timeout=10)
                    response.raise_for_status()
                except requests.RequestException as e:
                    logger.error(f"Ошибка запроса к hh.ru для employer_id {employer_id}: {e}")
                    break
                data = response.json()
                items = data.get("items", [])
                if not items:
                    logger.info(f"Нет вакансий для employer_id {employer_id} на странице {page}")
                    break
                all_vacancies.extend(items)
                logger.info(f"Получено {len(items)} вакансий с страницы {page} для employer_id {employer_id}")
                if page >= data.get("pages", 1) - 1:
                    break
                page += 1
                time.sleep(0.25)  # пауза, чтобы не превышать лимит API
        logger.info(f"Всего получено {len(all_vacancies)} вакансий от {len(employers_list)} работодателей.")
        return all_vacancies

    def _make_request(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Вспомогательный метод для отправки запроса и обработки исключений."""
        try:
            response = requests.get(self.base_url, params=params)
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при соединении с API: {e}")
            return None

    def _handle_response(self, response: requests.Response) -> Any | None:
        """Вспомогательный метод, проверяющий status_code и возвращающий json или None."""
        if response.status_code == 200:
            return response.json()
        else:
            logger.warning(f"Ошибка API: статус {response.status_code}")
            return None


logger.info("Модуль api.py завершил выполнение без ошибок.")
