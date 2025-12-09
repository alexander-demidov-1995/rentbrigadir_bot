"""
Пакет сервисов для Telegram бота.

Содержит модули с бизнес-логикой и утилитами.
"""

from .notifications import *

__all__ = [
    'notify_admins_about_new_application',
    'notify_application_processed'
]