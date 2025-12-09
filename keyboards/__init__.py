"""
Пакет клавиатур для Telegram бота.

Содержит модули для создания пользовательских
и административных клавиатур.
"""

from .user_kb import *
from .admin_kb import *

__all__ = [
    # user_kb
    'main_keyboard', 'categories_keyboard', 'tools_keyboard', 
    'tool_detail_keyboard', 'cancel_application_keyboard', 'confirmation_keyboard',
    
    # admin_kb
    'application_actions_keyboard', 'applications_list_keyboard', 'admin_main_keyboard'
]