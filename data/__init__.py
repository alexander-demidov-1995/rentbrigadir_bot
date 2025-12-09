"""
Пакет данных и конфигурации для Telegram бота.

Содержит модули с настройками и конфигурационными параметрами.
"""

from .config import *

__all__ = [
    'BOT_TOKEN',
    'ADMIN_IDS', 
    'DATABASE_URL',
    'DATABASE_PATH',
    'CSV_FILE_PATH'
]