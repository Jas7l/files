import os
import logging
from datetime import datetime
from typing import Optional
from tests.config.settings import settings

class Logger:
    """Класс для логирования тестов"""

    _loggers: dict = {}

    @staticmethod
    def get_logger(
        name: str,
        log_level: Optional[str] = None,
        log_file: Optional[str] = None,
    ) -> logging.Logger:
        """Создаёт или возвращает экземпляр логгера"""

        if name in Logger._loggers:
            return Logger._loggers[name]

        logger = logging.getLogger(name)

        if logger.hasHandlers():
            return logger

        logger.setLevel(log_level or settings.log_level)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level or "INFO")
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        if log_file is None:
            logs_dir = os.path.join(
                os.path.dirname(__file__), "..", "logs"
            )
            os.makedirs(logs_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = os.path.join(logs_dir, f"test_{timestamp}.log")

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level or "INFO")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        Logger._loggers[name] = logger
        return logger

def get_logger(name: str, log_level: Optional[str] = None) -> logging.Logger:
    """Инстанс логгера"""

    return Logger.get_logger(name, log_level)
