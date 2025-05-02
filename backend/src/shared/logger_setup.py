import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler

from src.shared.config import settings


def setup_logger(name:str, console: bool = False)->logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Вывод в консоль
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Создаем директорию для логов, если она не существует
    os.makedirs(settings.log_dir, exist_ok=True)

    # Вывод в файл с ротацией
    file_handler = TimedRotatingFileHandler(
        settings.log_file,
        when="midnight",
        interval=1,
        backupCount=7
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger