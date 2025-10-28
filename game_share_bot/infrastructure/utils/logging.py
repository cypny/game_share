import logging
import sys
from pathlib import Path


def setup_logging():
    """Настройка логирования для проекта"""

    # Создаем папку для логов если её нет
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Форматтер для логов
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Хендлер для файла
    file_handler = logging.FileHandler(
        filename=log_dir / "bot.log",
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # Хендлер для консоли
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)

    # Настраиваем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Уменьшаем verbosity для некоторых библиотек
    logging.getLogger('aiogram').setLevel(logging.INFO)
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.INFO)
    logging.getLogger('apscheduler').setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """Получить логгер с указанным именем"""
    return logging.getLogger(name)