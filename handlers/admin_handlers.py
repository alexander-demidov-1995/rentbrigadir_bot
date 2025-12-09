"""
Модуль обработчиков для административной панели.
"""

from aiogram import types, F
from aiogram.filters import Command

from data.config import ADMIN_IDS
from database import db
from keyboards.admin_kb import (admin_main_keyboard, applications_list_keyboard, 
                               application_actions_keyboard)

async def admin_panel(message: types.Message):
    """Показывает панель администратора."""
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ Доступ запрещен")
        return
    
    admin_text = (
        "👨‍💼 <b>Панель администратора RentBrigadir</b>\n\n"
        "Здесь вы можете:\n"
        "• 📋 Просматривать новые заявки\n"
        "• ✅ Отмечать заявки как обработанные\n"
        "• 📞 Быстро звонить клиентам\n"
        "• 📊 Смотреть статистику\n\n"
        "Выберите действие ниже 👇"
    )
    await message.answer(admin_text, reply_markup=admin_main_keyboard(), parse_mode="HTML")

async def show_new_applications(callback: types.CallbackQuery):
    """Показывает список новых заявок."""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Доступ запрещен")
        return
    
    applications = db.get_new_applications()
    
    if not applications:
        await callback.message.edit_text(
            "📭 <b>Новых заявок нет</b>\n\n"
            "Все заявки обработаны! 🎉",
            reply_markup=admin_main_keyboard(),
            parse_mode="HTML"
        )
        return
    
    await callback.message.edit_text(
        f"📋 <b>Новые заявки</b> ({len(applications)}):",
        reply_markup=applications_list_keyboard(applications),
        parse_mode="HTML"
    )
    await callback.answer()

async def show_all_applications(callback: types.CallbackQuery):
    """Показывает все заявки."""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Доступ запрещен")
        return
    
    # Получаем все заявки
    db.cursor.execute('''
        SELECT a.*, u.username, u.full_name as user_full_name 
        FROM applications a 
        LEFT JOIN users u ON a.user_id = u.id 
        ORDER BY a.application_date DESC LIMIT 15
    ''')
    applications = db.cursor.fetchall()
    
    if not applications:
        await callback.message.edit_text(
            "📭 <b>Заявок нет</b>",
            reply_markup=admin_main_keyboard(),
            parse_mode="HTML"
        )
        return
    
    await callback.message.edit_text(
        f"📋 <b>Последние заявки</b> ({len(applications)}):",
        reply_markup=applications_list_keyboard(applications),
        parse_mode="HTML"
    )
    await callback.answer()

async def show_application_detail(callback: types.CallbackQuery):
    """Показывает детальную информацию о заявке."""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Доступ запрещен")
        return
    
    application_id = int(callback.data.split("_")[2])
    application = db.get_application_by_id(application_id)
    
    if not application:
        await callback.message.edit_text("❌ Заявка не найдена")
        await callback.answer()
        return
    
    app_id, user_id, service_name, rental_period, app_date, customer_name, phone, status, username, user_full_name = application
    
    detail_text = (
        f"📋 <b>Заявка #{app_id}</b>\n\n"
        f"<b>Инструмент:</b> {service_name}\n"
        f"<b>Срок аренды:</b> {rental_period}\n"
        f"<b>Клиент:</b> {customer_name}\n"
        f"<b>Телефон:</b> {phone}\n"
        f"<b>Дата:</b> {app_date}\n"
        f"<b>Username:</b> @{username if username else 'нет'}\n"
        f"<b>User ID:</b> {user_id}\n"
        f"<b>Статус:</b> {status}"
    )
    
    await callback.message.edit_text(
        detail_text,
        reply_markup=application_actions_keyboard(app_id),
        parse_mode="HTML"
    )
    await callback.answer()

async def mark_application_processed(callback: types.CallbackQuery):
    """Помечает заявку как обработанную."""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Доступ запрещен")
        return
    
    application_id = int(callback.data.split("_")[2])
    db.mark_application_processed(application_id)
    
    await callback.message.edit_text(
        f"✅ <b>Заявка #{application_id} отмечена как обработанная</b>",
        reply_markup=admin_main_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

async def call_customer(callback: types.CallbackQuery):
    """Показывает номер телефона клиента."""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Доступ запрещен")
        return
    
    application_id = int(callback.data.split("_")[2])
    application = db.get_application_by_id(application_id)
    
    if application:
        phone = application[6]
        customer_name = application[5]
        
        await callback.answer(
            f"📞 Телефон клиента {customer_name}: {phone}",
            show_alert=True
        )

async def show_admin_stats(callback: types.CallbackQuery):
    """Показывает статистику."""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Доступ запрещен")
        return
    
    # Получаем статистику
    db.cursor.execute('''
        SELECT 
            COUNT(*) as total_applications,
            SUM(CASE WHEN status = 'new' THEN 1 ELSE 0 END) as new_applications,
            SUM(CASE WHEN status = 'processed' THEN 1 ELSE 0 END) as processed_applications,
            COUNT(DISTINCT user_id) as unique_customers
        FROM applications
    ''')
    stats = db.cursor.fetchone()
    
    if stats:
        total, new, processed, unique_customers = stats
        
        stats_text = (
            "📊 <b>Статистика заявок</b>\n\n"
            f"• Всего заявок: <b>{total}</b>\n"
            f"• Новые заявки: <b>{new}</b>\n"
            f"• Обработанные: <b>{processed}</b>\n"
            f"• Уникальных клиентов: <b>{unique_customers}</b>\n\n"
            f"• Эффективность обработки: <b>{(processed/total*100) if total > 0 else 0:.1f}%</b>"
        )
    else:
        stats_text = "📊 <b>Статистика недоступна</b>"
    
    await callback.message.edit_text(stats_text, parse_mode="HTML")
    await callback.answer()

async def refresh_applications(callback: types.CallbackQuery):
    """Обновляет список заявок."""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Доступ запрещен")
        return
    
    applications = db.get_new_applications()
    
    if not applications:
        await callback.message.edit_text(
            "📭 <b>Новых заявок нет</b>\n\n"
            "Все заявки обработаны! 🎉",
            reply_markup=admin_main_keyboard(),
            parse_mode="HTML"
        )
        return
    
    await callback.message.edit_text(
        f"📋 <b>Новые заявки</b> ({len(applications)}):",
        reply_markup=applications_list_keyboard(applications),
        parse_mode="HTML"
    )
    await callback.answer()

async def back_to_admin(callback: types.CallbackQuery):
    """Возвращает в админ-панель."""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Доступ запрещен")
        return
    
    await callback.message.edit_text(
        "👨‍💼 <b>Панель администратора RentBrigadir</b>\n\n"
        "Выберите действие ниже 👇",
        reply_markup=admin_main_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()