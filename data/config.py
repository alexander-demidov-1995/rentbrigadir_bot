"""
Модуль конфигурации бота.

Загружает переменные окружения и предоставляет константы для использования во всем проекте.
Безопасное хранение чувствительных данных BOT_TOKEN.
"""

import os
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

# Конфигурационные константы
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден в переменных окружения. Проверьте файл .env")

# Список ID администраторов (Telegram ID администраторов, через запятую)
ADMIN_IDS = [377858450]

# Настройки базы данных
DATABASE_URL = "sqlite:///database.db"
DATABASE_PATH = "database.db"

# Настройки путей
CSV_FILE_PATH = "tools.csv"

print("✅ Конфигурация загружена успешно")