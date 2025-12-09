"""
Модуль клавиатур для пользовательского интерфейса.
"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_keyboard():
    """
    Создает главную reply-клавиатуру бота.
    """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔧 Инструменты")],
            [KeyboardButton(text="📝 Оставить заявку"), KeyboardButton(text="🚚 Доставка")],
            [KeyboardButton(text="📞 Контакты"), KeyboardButton(text="ℹ️ Помощь")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
    )
    return keyboard

def categories_keyboard(categories):
    """
    Создает inline-клавиатуру с категориями инструментов.
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    
    # ИСПРАВЛЯЕМ РАСПАКОВКУ - теперь только 2 значения
    for category in categories:
        category_id = category[0]  # id
        name = category[1]         # name
        # emoji больше нет - убрали category[2]
        
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=name,
                callback_data=f"category_{category_id}"
            )
        ])
    
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="Назад", callback_data="back_to_main")
    ])
    
    return keyboard

def tools_keyboard(tools):
    """
    Создает inline-клавиатуру со списком инструментов.
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    
    # УБИРАЕМ ОГРАНИЧЕНИЕ [8] - показываем ВСЕ инструменты
    for tool in tools:  # Без [:8]
        tool_id = tool[0]
        name = tool[1]
        price_1_day = tool[4]
        
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"{name} - {price_1_day}₽/день",
                callback_data=f"tool_{tool_id}"
            )
        ])
    
    # Навигационные кнопки
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="🔙 К категориям", callback_data="back_to_categories")
    ])
    
    return keyboard

def tool_detail_keyboard(tool_id):
    """
    Создает inline-клавиатуру для детальной страницы инструмента.
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="📝 Арендовать этот инструмент",
                callback_data=f"rent_{tool_id}"
            )],
            [InlineKeyboardButton(
                text="🔙 К списку инструментов",
                callback_data="back_to_tools"
            )]
        ]
    )
    return keyboard

def cancel_application_keyboard():
    """
    Создает inline-клавиатуру для отмены заявки.
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="🔙 Назад к инструментам",
                callback_data="cancel_to_tools"
            )]
        ]
    )
    return keyboard

def confirmation_keyboard():
    """
    Создает inline-клавиатуру для подтверждения заявки.
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да, отправить", callback_data="confirm_application"),
                InlineKeyboardButton(text="✏️ Нет, изменить", callback_data="edit_application")
            ],
            [InlineKeyboardButton(text="🔙 Назад к инструментам", callback_data="cancel_to_tools")]
        ]
    )
    return keyboard