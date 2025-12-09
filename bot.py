"""
Главный модуль Telegram-бота для арендной компании "RentBrigadir".
"""

import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

# Импорт конфигурации
from data.config import BOT_TOKEN

# Импорт базы данных
from database import db

# Импорт обработчиков
from handlers.user_handlers import (
    cmd_start, cmd_help, cmd_contacts, cmd_delivery, cmd_catalog,
    show_categories, show_contacts, show_delivery_info, show_help,
    show_tools_by_category, show_tool_detail, back_to_categories, 
    back_to_main, back_to_tools, cancel_to_tools
)

from handlers.application_handlers import (
    ApplicationStates, start_application, rent_tool, process_tool_name,
    process_rental_period, process_customer_name, process_phone,
    confirm_application, edit_application, cancel_application
)

from handlers.admin_handlers import (
    admin_panel, show_new_applications, show_all_applications,
    show_application_detail, mark_application_processed, call_customer,
    show_admin_stats, refresh_applications, back_to_admin
)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

def register_handlers():
    """Регистрирует все обработчики команд и callback-запросов."""
    
    # Команды пользователя
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_help, Command("help"))
    dp.message.register(cmd_contacts, Command("contacts"))
    dp.message.register(cmd_delivery, Command("delivery"))
    dp.message.register(cmd_catalog, Command("catalog"))
    dp.message.register(cancel_application, Command("cancel"))
    
    # Админ команды
    dp.message.register(admin_panel, Command("admin"))
    
    # Обработчики текстовых сообщений (главное меню)
    dp.message.register(show_categories, F.text == "🔧 Инструменты")
    dp.message.register(start_application, F.text == "📝 Оставить заявку")
    dp.message.register(show_delivery_info, F.text == "🚚 Доставка")
    dp.message.register(show_contacts, F.text == "📞 Контакты")
    dp.message.register(show_help, F.text == "ℹ️ Помощь")
    
    # Обработчики callback-запросов (инструменты)
    dp.callback_query.register(show_tools_by_category, F.data.startswith("category_"))
    dp.callback_query.register(show_tool_detail, F.data.startswith("tool_"))
    dp.callback_query.register(rent_tool, F.data.startswith("rent_"))
    dp.callback_query.register(back_to_categories, F.data == "back_to_categories")
    dp.callback_query.register(back_to_main, F.data == "back_to_main")
    dp.callback_query.register(back_to_tools, F.data == "back_to_tools")  
    dp.callback_query.register(cancel_to_tools, F.data == "cancel_to_tools")
    
    # Обработчики состояний FSM (заявки)
    dp.message.register(process_tool_name, ApplicationStates.waiting_for_tool_name)
    dp.message.register(process_rental_period, ApplicationStates.waiting_for_rental_period)
    dp.message.register(process_customer_name, ApplicationStates.waiting_for_customer_name)
    dp.message.register(process_phone, ApplicationStates.waiting_for_phone)
    
    # Обработчики подтверждения заявки
    dp.callback_query.register(confirm_application, F.data == "confirm_application")
    dp.callback_query.register(edit_application, F.data == "edit_application")
    
    # Админ обработчики callback-запросов
    dp.callback_query.register(show_new_applications, F.data == "new_applications")
    dp.callback_query.register(show_all_applications, F.data == "all_applications")
    dp.callback_query.register(show_application_detail, F.data.startswith("app_detail_"))
    dp.callback_query.register(mark_application_processed, F.data.startswith("app_processed_"))
    dp.callback_query.register(call_customer, F.data.startswith("app_call_"))
    dp.callback_query.register(show_admin_stats, F.data == "admin_stats")
    dp.callback_query.register(refresh_applications, F.data == "refresh_applications")
    dp.callback_query.register(back_to_admin, F.data == "back_to_admin")

async def main():
    """Основная функция для запуска бота."""
    # Инициализация подключения к базе данных
    db.connect()
    print("✅ База данных подключена успешно")
    
    # Регистрация всех обработчиков
    register_handlers()
    print("✅ Обработчики зарегистрированы")
    
    # Запуск бота
    print("🚀 Бот запущен! Ожидание сообщений...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())