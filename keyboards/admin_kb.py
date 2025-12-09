"""
Модуль клавиатур для административного интерфейса.

Содержит функции для создания inline-клавиатур,
используемых в админ-панели для управления заявками.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def application_actions_keyboard(application_id):
    """
    Создает клавиатуру действий для конкретной заявки.
    
    Args:
        application_id (int): ID заявки
        
    Returns:
        InlineKeyboardMarkup: Клавиатура с действиями администратора
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Обработано", 
                    callback_data=f"app_processed_{application_id}"
                ),
                InlineKeyboardButton(
                    text="📞 Позвонить", 
                    callback_data=f"app_call_{application_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📋 Все заявки", 
                    callback_data="all_applications"
                ),
                InlineKeyboardButton(
                    text="🔄 Обновить", 
                    callback_data="refresh_applications"
                )
            ]
        ]
    )
    return keyboard

def applications_list_keyboard(applications):
    """
    Создает клавиатуру со списком заявок.
    
    Args:
        applications (list): Список заявок из БД
        
    Returns:
        InlineKeyboardMarkup: Клавиатура со списком заявок
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    
    # Добавляем кнопки для каждой заявки (максимум 10)
    for app in applications[:10]:
        app_id, user_id, service_name, rental_period, app_date, customer_name, phone, status, username, user_full_name = app
        
        # Обрезаем длинные названия для удобства отображения
        display_name = service_name[:20] + "..." if len(service_name) > 20 else service_name
        
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"#{app_id} {display_name} - {customer_name}", 
                callback_data=f"app_detail_{app_id}"
            )
        ])
    
    # Добавляем кнопку возврата
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_admin")
    ])
    
    return keyboard

def admin_main_keyboard():
    """
    Создает главную клавиатуру админ-панели.
    
    Returns:
        InlineKeyboardMarkup: Основная клавиатура администратора
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="📋 Новые заявки", 
                callback_data="new_applications"
            )],
            [InlineKeyboardButton(
                text="📊 Статистика", 
                callback_data="admin_stats"
            )]
        ]
    )
    return keyboard