"""
Модуль логирования с поддержкой русского и английского языков.
Logging module with Russian and English language support.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


class BilingualFormatter(logging.Formatter):
    """Форматтер для логов на двух языках | Formatter for bilingual logs"""

    def format(self, record):
        # Добавляем timestamp в читаемом формате
        record.timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        return super().format(record)


def setup_logger(name: str = "gorun", level: int = logging.INFO) -> logging.Logger:
    """
    Настройка логгера с выводом в консоль и файл.
    Setup logger with console and file output.

    Args:
        name: Имя логгера | Logger name
        level: Уровень логирования | Logging level

    Returns:
        Настроенный логгер | Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Избегаем дублирования handlers
    if logger.handlers:
        return logger

    # Формат логов | Log format
    log_format = '%(timestamp)s | %(levelname)-8s | %(name)s | %(message)s'
    formatter = BilingualFormatter(log_format)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    log_dir = Path(__file__).resolve().parent / "logs"
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / f"gorun_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


# Создаем основной логгер приложения | Create main application logger
app_logger = setup_logger("gorun.app")
auth_logger = setup_logger("gorun.auth")
chat_logger = setup_logger("gorun.chat")
friend_logger = setup_logger("gorun.friend")
run_logger = setup_logger("gorun.run")
db_logger = setup_logger("gorun.db")
ws_logger = setup_logger("gorun.websocket")
